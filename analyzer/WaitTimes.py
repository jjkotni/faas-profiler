import pdb
from PerfMonAnalyzer import ReadPerfMon
from ContactDB import GetActivation
from WorkloadAnalyzer import ExtractExtraAnnotations
import matplotlib.pyplot as plt
import pandas as pd

def GetMetadata(test_name):
    """
    Returns the test start time from the output log of SWI.
    """
    test_start_time = None
    with open("logs/" + test_name + "/activationIds.out") as f:
        lines = f.read().splitlines()
        return lines 

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
        # perf_data['statusCode'].append(activation['response']['statusCode'])
    return pd.DataFrame(perf_data)


def func(test_name, rate):
    lines = GetMetadata(test_name)
    test_df = ConstructTestDataframe(lines)

    #waitTime is the difference between the time at which an event was triggered and the time at which 
    #the function started executing. Hence, waitTime = startTime-invokeTime.
    test_df['invokeTime'] = test_df['start'] - test_df['waitTime']
    firstInvoke = test_df['invokeTime'].min()
    test_df['invokeTimeRel'] = (test_df['invokeTime'] - firstInvoke)/1000.0	
    requested_frame = test_df[['invokeTimeRel', 'waitTime']].sort_values('invokeTimeRel', ascending=True);
    return requested_frame 

def main():
    axes =[]
    plt.figure()
#    for i in [45]: #gap between expts
#        for j in [3,6, 9, 12, 15, 18, 21, 24, 27, 30, 40, 50, 75, 100, 125 ]: #rate of invocation
    for idx, i in enumerate([30]): #gap between expts
        for k in [1,2,3,4,5]: #run number
            axes = None
            for j in [3,6, 9, 12, 15, 18, 21, 24, 27, 30, 40, 50, 75, 100, 125]: #rate of invocation
                test_name = "wt_" + str(k) + "_" + str(j) + "_" + str(i)
                df = func(test_name,j)
                label=str(j)
                if axes is None:
                    axes = df.plot(y='waitTime',x='invokeTimeRel', label=label)
                else:
                    df.plot(y='waitTime',x='invokeTimeRel', label=label, ax=axes)

            img = "plots/wait-time-" + str(k) + ".png"
            plt.ylabel("Wait Time")
            plt.xlabel("Time")
            plt.legend(title="Invocation Rate")
            plt.savefig(img)
            plt.close()
            plt.figure()

if __name__== "__main__":
  main()
