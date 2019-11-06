#!/usr/bin/env python3.6

# Copyright (c) 2019 Princeton University
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Standard imports
import json
from optparse import OptionParser
import os
import requests
from concurrent.futures import ProcessPoolExecutor
from requests_futures.sessions import FuturesSession
import subprocess
import sys
import time
import threading
import logging
import pdb

# Local imports
sys.path = ['./', '../'] + sys.path
from GenConfigs import *
sys.path = [FAAS_ROOT + '/synthetic-workload-invoker'] + sys.path
from EventGenerator import GenericEventGenerator
from commons.JSONConfigHelper import CheckJSONConfig, ReadJSONConfig
from commons.Logger import ScriptLogger
from WorkloadChecker import CheckWorkloadValidity
from pathlib import Path

logging.captureWarnings(True)

# Global variables
supported_distributions = {'Poisson', 'Uniform'}

APIHOST = 'https://172.17.0.1'
print(WSK_PATH)
AUTH_KEY = subprocess.check_output(WSK_PATH + " property get --auth", shell=True).split()[2]
AUTH_KEY = AUTH_KEY.decode("utf-8")
user_pass = AUTH_KEY.split(':')
NAMESPACE = '_'
RESULT = 'false'
base_url = APIHOST + '/api/v1/namespaces/' + NAMESPACE + '/actions/'
base_gust_url = APIHOST + '/api/v1/web/guest/default/'

param_file_cache = {}   # a cache to keep json of param files
binary_data_cache = {}  # a cache to keep binary data (image files, etc.)


def PROCESSInstanceGenerator(instance, instance_script, instance_times, blocking_cli):
    if len(instance_times) == 0:
        return False
    after_time, before_time = 0, 0

    if blocking_cli:
        pass
    else:
        instance_script = instance_script + ' &'

    for t in instance_times:
        time.sleep(max(0, t - (after_time - before_time)))
        before_time = time.time()
        os.system(instance_script)
        after_time = time.time()

    return True


def HTTPInstanceGenerator(action, instance_times, blocking_cli, log_dir, param_file=None):
    if len(instance_times) == 0:
        return False
    url = base_url + action
    session = FuturesSession(max_workers=15)
    after_time, before_time = 0, 0
    invoke_records = []

    if param_file == None:
        for t in instance_times:
            st = t - (after_time - before_time)
            if st > 0:
                time.sleep(st)
            before_time = time.time()
            future = session.post(url, params={'blocking': blocking_cli, 'result': RESULT}, auth=(
                user_pass[0], user_pass[1]), verify=False)
            after_time = time.time()
    else:   # if a parameter file is provided
        try:
            param_file_body = param_file_cache[param_file]
        except:
            with open(param_file, 'r') as f:
                param_file_body = json.load(f)
                param_file_cache[param_file] = param_file_body

        for t in instance_times:
            st = t - (after_time - before_time)
            if st > 0:
                time.sleep(st)
            before_time = time.time()
            future = session.post(url, params={'blocking': blocking_cli, 'result': RESULT}, auth=(
                user_pass[0], user_pass[1]), json=param_file_body, verify=False)
            
            post_response = json.loads(future.result().content.decode())
            post_response['invoke_time'] = before_time  
            pdb.set_trace()   
            invoke_records.append(post_response['activationId'])   
            after_time = time.time()

    activations_file = FAAS_ROOT+'/'+log_dir+'/activationIds.out'
    pdb.set_trace()
    with open(activations_file, 'a') as f:
        np.savetxt(f, invoke_records, delimiter=',')

    return True


def BinaryDataHTTPInstanceGenerator(action, instance_times, blocking_cli, data_file):
    """
    TODO: Automate content type
    """
    url = base_gust_url + action
    session = FuturesSession(max_workers=15)
    if len(instance_times) == 0:
        return False
    after_time, before_time = 0, 0

    try:
        data = binary_data_cache[data_file]
    except:
        data = open(data_file, 'rb').read()
        binary_data_cache[data_file] = data

    for t in instance_times:
        st = t - (after_time - before_time)
        if st > 0:
            time.sleep(st)
        before_time = time.time()
        session.post(url=url, headers={'Content-Type': 'image/jpeg'},
                     params={'blocking': blocking_cli, 'result': RESULT},
                     data=data, auth=(user_pass[0], user_pass[1]), verify=False)
        after_time = time.time()

    return True

def ApplyJSONOverrides(workload, workloadOverrides, instanceOverrides):
    workload.update(workloadOverrides)

    for (instance, desc) in workload['instances'].items():
        desc.update(instanceOverrides)
        workload['instances'][instance] = desc

    return workload

def createDir(test_name):
    log_dir = 'logs/' + test_name

    if not os.path.exists(FAAS_ROOT + '/' + log_dir):
        os.makedirs(log_dir, 0o777)

    log_file = log_dir+'/SWI.log'
    Path(FAAS_ROOT + '/' + log_file).touch()
    os.chmod(log_file, 0o777)

    return log_dir, log_file

def main(argv):
    """
    The main function.
    """
    parser = OptionParser()
    parser.add_option("-n", "--test_name", dest="test_name", default="latest_test",
                      help="Name of test", metavar="FILE")
    parser.add_option("-r", "--rate_override", dest="rate_override",
                      help="Override rate of invocation from arguments", metavar="FILE")
    parser.add_option("-c", "--config_json", dest="config_json",
                      help="The input json config file describing the synthetic workload.", metavar="FILE")
    (options, args) = parser.parse_args()

    log_dir, log_file = createDir(options.test_name)
    logger  = ScriptLogger('workload_invoker', log_file)

    logger.info("Workload Invoker started")

    print("Log file -> ", log_file,"\n")

    if not CheckJSONConfig(options.config_json):
        logger.error("Invalid or no JSON config file!")
        return False    # Abort the function if json file not valid

    workloadOverrides = {}
    workloadOverrides['log_dir'] = log_dir
    instanceOverrides = {}
    if(options.rate_override != None):
        instanceOverrides['rate'] = int(options.rate_override)

    workload = ReadJSONConfig(options.config_json)
    workload = ApplyJSONOverrides(workload,workloadOverrides, instanceOverrides)

    if not CheckWorkloadValidity(workload=workload, supported_distributions=supported_distributions):
        return False    # Abort the function if json file not valid


    [all_events, event_count] = GenericEventGenerator(workload)

    threads = []

    for (instance, instance_times) in all_events.items():
        # Previous method to run processes
        # instance_script = 'bash ' + FAAS_ROOT + '/invocation-scripts/' + \
        #     workload['instances'][instance]['application']+'.sh'
        # threads.append(threading.Thread(target=PROCESSInstanceGenerator, args=[instance, instance_script, instance_times, workload['blocking_cli']]))
        # New method
        action = workload['instances'][instance]['application']
        try:
            param_file = workload['instances'][instance]['param_file']
        except:
            param_file = None
        blocking_cli = workload['blocking_cli']
        if 'data_file' in workload['instances'][instance].keys():
            data_file = workload['instances'][instance]['data_file']
            threads.append(threading.Thread(target=BinaryDataHTTPInstanceGenerator, args=[
                           action, instance_times, blocking_cli, data_file]))
        else:
            threads.append(threading.Thread(target=HTTPInstanceGenerator, args=[
                           action, instance_times, blocking_cli, log_dir, param_file ]))
        pass

    # Dump Test Metadata
    metadata_file = log_dir + "/test_metadata.out"
    os.system("date +%s%N | cut -b1-13 > "           + FAAS_ROOT + '/' + metadata_file)
    os.system("echo " + options.config_json + " >> " + FAAS_ROOT + '/' + metadata_file)
    os.system("echo " + str(event_count) + " >> "    + FAAS_ROOT + '/' + metadata_file)

    try:
        if workload['perf_monitoring']['runtime_script']:
            runtime_script = 'bash ' + FAAS_ROOT + '/' + workload['perf_monitoring']['runtime_script'] + \
                ' ' + str(int(workload['test_duration_in_seconds'])) + ' ' + FAAS_ROOT + '/' + log_dir + '/perf-mon.out' + ' &'
            logger.info(runtime_script)
            os.system(runtime_script)
            logger.info("Runtime monitoring script ran")
    except:
        pass

    logger.info("Test started")
    for thread in threads:
        thread.start()
    logger.info("Test ended")

    return True


if __name__ == "__main__":
    main(sys.argv)
