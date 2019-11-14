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

def func(test_name):
    lines = GetMetadata(test_name)
    test_df = ConstructTestDataframe(lines)

    #waitTime is the difference between the time at which an event was triggered and the time at which 
    #the function started executing. Hence, waitTime = startTime-invokeTime.
    test_df['executionTime'] = test_df['duration'] - test_df['initTime']
    test_df['invokeTime'] = test_df['start'] - test_df['waitTime']
    test_df['latency'] = test_df['duration'] + test_df['waitTime']
    firstInvoke = test_df['invokeTime'].min()
    test_df['invokeTimeRel'] = (test_df['invokeTime'] - firstInvoke)/1000.0	
    requested_frame = test_df[['invokeTimeRel', 'latency', 'executionTime']].sort_values('invokeTimeRel', ascending=True)
    return requested_frame 

def main(benchmark, machine):
    runs = [1,2]
    threads = [4,8,10]

    axes =[]
    plt.figure()

    img_dir = os.environ['FAAS_ROOT'] + "/plots/" + machine + "/mt_roi/" + benchmark

    if not os.path.exists(img_dir):
        os.makedirs(img_dir, 0o777)

    qos_results = {'single_thread':[], 'multi_thread':[], 'num_threads':[], 'qos_improvement':[]}
    execution_time = {'single_thread':[], 'multi_thread':[], 'num_threads':[]}

    for j in threads: #number of threads
        balanced_test_name = machine + "/balanced_roi/" + benchmark + "/1_" + str(10*j)
        balanced_df = func(balanced_test_name)
        single_thread_QoS = balanced_df['latency'].quantile(0.99)
        label= str(10*j) + ",1"
        axes = balanced_df.plot(y='latency',x='invokeTimeRel', label=label)

        execution_time['num_threads'].append(j)
        execution_time['single_thread'].append(balanced_df['executionTime'].quantile(0.99))

        multi_thread_QoS = 0
        multi_thread_execution_time = 0
        for k in runs: #run number
            mt_test_name = machine + "/mt_roi/" + benchmark + "/" + str(k) + "_" + str(j)
            try:
                df = func(mt_test_name)
                label="10, "+ str(j)
                multi_thread_execution_time += df['executionTime'].quantile(0.99)
                multi_thread_QoS += df['latency'].quantile(0.99)
                df.plot(y='latency', x='invokeTimeRel', label=label, ax=axes)
            except Exception as e:
                print("Plot failed for run ", str(k), ", ROI ", str(j))
                print(e)

        multi_thread_execution_time = multi_thread_execution_time/(1.0*len(runs)*j)
        execution_time['multi_thread'].append(multi_thread_execution_time)
        multi_thread_QoS = multi_thread_QoS/(1.0*len(runs))
        qos_results['num_threads'].append(j)
        qos_results['single_thread'].append(single_thread_QoS)
        qos_results['multi_thread'].append(multi_thread_QoS)
        qos_results['qos_improvement'].append((100.0*(single_thread_QoS-multi_thread_QoS)/multi_thread_QoS))

        img = img_dir + "/latency_" + str(j) + ".png"
        plt.ylabel("Total Latency")
        plt.xlabel("Time")
        plt.legend(title="(IPS, Workers)")
        plt.savefig(img)
        plt.close()
        plt.figure()

    execution_time = pd.DataFrame(execution_time)
    et_axes = execution_time.plot(y='single_thread', x='num_threads', c = 'red', label='Single Thread', marker='o')
    execution_time.plot(y='multi_thread', x='num_threads', c = 'green', ax=et_axes, label='Multi Thread', marker='o')

    for i, val in enumerate(execution_time['num_threads']):
        et_axes.annotate(str(round(execution_time['single_thread'][i],2)), (val,execution_time['single_thread'][i] ))
        et_axes.annotate(str(round(execution_time['multi_thread'][i],2)), (val,execution_time['multi_thread'][i] ))

    img = img_dir + "/ExecutionTime.png"
    plt.ylabel("99%ile Cost per user")
    plt.xlabel("No. of workers")
    plt.legend(title="Container Type")
    plt.savefig(img)
    plt.close()
    plt.figure()

    qos_results = pd.DataFrame(qos_results)
    qos_axes = qos_results.plot(y='qos_improvement', x='num_threads', marker='o')
    
    for i, val in enumerate(qos_results['qos_improvement']):
        qos_axes.annotate(str(round(val,2))+"%", (qos_results['num_threads'][i], qos_results['qos_improvement'][i]))

    img = img_dir + "/QoS.png"
    plt.ylabel("QoS Improvement(%)")
    plt.xlabel("Number of Threads")
    plt.savefig(img)
    plt.close()
    plt.figure()


    pd.DataFrame(qos_results).to_csv()

if __name__== "__main__":
    parser = OptionParser()
    parser.add_option("-b", "--benchmark", dest="benchmark", metavar="FILE")
    parser.add_option("-m", "--machine",   dest="machine",   metavar="FILE")
    (options, args) = parser.parse_args()

    main(options.benchmark, options.machine)
