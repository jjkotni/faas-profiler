import pdb
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

sys.path = ['.', '../', os.environ['FAAS_ROOT']+'/workload-analyzer'] + sys.path

import importlib
fabfile = importlib.import_module('workload-analyzer.PerfMonAnalyzer', 'ReadPerfMon')

#from workloadPerfMonAnalyzer import ReadPerfMon
from ContactDB import GetActivation
from WorkloadAnalyzer import ExtractExtraAnnotations
from optparse import OptionParser

current_bmk = ''

def GetMetadata(test_name):
    """
    Returns the test start time from the output log of SWI.
    """
    test_start_time = None
    
    with open(os.environ['FAAS_ROOT'] +"/logs/" + test_name + "/activationIds.out") as f:
        lines = f.read().splitlines()
        return lines

def filterActivations(activations):
    filteredActivations=[]
    failedActivations = 0
    for activation in activations:
        if('error' in activation['response']['result']):
            failedActivations += 1
        else:
            filteredActivations.append(activation)

    print("Failed activations: ", str(failedActivations), "\n");
    return filteredActivations

def ConstructTestDataframe(activationIds):
    """
    Constructs a dataframe for the performance information of all invocations.
    """
    perf_data = {'func_name': [], 'activationId': [], 'start': [], 'end': [
    ], 'duration': [], 'waitTime': [], 'initTime': [], 'latency': [], 'lang': []}

    perf_data['results'] = []

    activations = []
    for id in activationIds:
        activations.append(GetActivation(id))

    activations = filterActivations(activations)

    for activation in activations:
        perf_data['func_name'].append(activation['name'])
        perf_data['activationId'].append(activation['_id'])
        perf_data['start'].append(activation['start'])
        perf_data['end'].append(activation['end'])
        perf_data['duration'].append(activation['duration'])
        extra_data = ExtractExtraAnnotations(
            activation['annotations'])
        perf_data['waitTime'].append(extra_data['waitTime'])
        perf_data['initTime'].append(extra_data['initTime'])
        perf_data['lang'].append(extra_data['kind'])
        perf_data['latency'].append(
            perf_data['duration'][-1]+perf_data['waitTime'][-1])
        perf_data['results'].append(activation['response']['result'])
    return pd.DataFrame(perf_data)

def func(test_name, rate):
    lines = GetMetadata(test_name)
    test_df = ConstructTestDataframe(lines)

    #waitTime is the difference between the time at which an event was triggered and the time at which 
    #the function started executing. Hence, waitTime = startTime-invokeTime.
    test_df['invokeTime'] = test_df['start'] - test_df['waitTime']
    test_df['latency'] = test_df['duration'] + test_df['waitTime']
    firstInvoke = test_df['invokeTime'].min()
    test_df['invokeTimeRel'] = (test_df['invokeTime'] - firstInvoke)/1000.0	
    requested_frame = test_df[['invokeTimeRel', 'latency']].sort_values('invokeTimeRel', ascending=True)
    return requested_frame 

def main(benchmark, machine):
    axes =[]
    plt.figure()

    img_dir = os.environ['FAAS_ROOT'] + "/plots/" + machine + "/e_times/" + benchmark

    if not os.path.exists(img_dir):
        os.makedirs(img_dir, 0o777)

    for k in [1]: #run number
        axes = None
        for j in [8]: #workers
            test_name    = machine + "/e_times/" + benchmark + "/" + str(k) + "_" + str(j)
            test_name_mt = machine + "/e_times/" + benchmark + "_mt/" + str(k) + "_" + str(j)
            try:
                df    = func(test_name,j)
                df_mt = func(test_name_mt,j)
                label=str(j)
                if axes is None:
                    axes = df.plot(y='latency',x='invokeTimeRel', label=label)
                    df_mt.plot(y='latency',x='invokeTimeRel', label=label, ax=axes)
                else:
                    df.plot(y='latency',x='invokeTimeRel', label=label, ax=axes)
                    df_mt.plot(y='latency',x='invokeTimeRel', label=label, ax=axes)
            except Exception as e:
                print("Plot failed for run ", str(k), ", ROI ", str(j))
                print(e)

        img = img_dir + "/latency_" + str(k) + ".png"
        plt.ylabel("Execution Latency")
        plt.xlabel("Time")
        plt.legend(title="Invocation Rate")
        plt.savefig(img)
        plt.close()
        plt.figure()

if __name__== "__main__":
    parser = OptionParser()
    parser.add_option("-b", "--benchmark", dest="benchmark", metavar="FILE")
    parser.add_option("-m", "--machine",   dest="machine",   metavar="FILE")
    (options, args) = parser.parse_args()

    main(options.benchmark, options.machine)
