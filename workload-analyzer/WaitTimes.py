import pdb
from PerfMonAnalyzer import ReadPerfMon
from WorkloadAnalyzer import ConstructTestDataframe
from ContactDB import GetActivationRecordsSince
import matplotlib.pyplot as plt
import pandas as pd
import pdb

def GetMetadata(test_name):
    """
    Returns the test start time from the output log of SWI.
    """
    test_start_time = None
    with open("logs/" + test_name + "/test_metadata.out") as f:
        lines = f.readlines()
        test_start_time = lines[0]
        config_file = lines[1]
        invoked_actions = int(lines[2][:-1])
        return int(test_start_time[:-1]),invoked_actions 


def func(test_name, rate):
    test_start_time, actions_invoked = GetMetadata(test_name)
    test_df = ConstructTestDataframe(since=test_start_time, limit= actions_invoked, 
                                    read_results=True)

    #waitTime is the difference between the time at which an event was triggered and the time at which 
    #the function started executing. Hence, waitTime = startTime-invokeTime.
    test_df['invokeTime'] = test_df['start'] - test_df['waitTime']
    firstInvoke = test_df['invokeTime'].min()
    test_def['invokeTimeRel'] = (test_df['invokeTime'] - firstInvoke)/1000.0	
    requested_frame = test_df[['invokeTimeRel', 'waitTime']].sort_values('invokeTimeRel', ascending=True);
    pdb.set_trace()  
    return requested_frame 

def main():
    axes =[]
    plt.figure()
    for i in [45]: #gap between expts
#        for j in [3,6, 9, 12, 15, 18, 21, 24, 27, 30, 40, 50, 75, 100, 125 ]: #rate of invocation
    for idx, i in enumerate([20, 45, 60, 120]): #gap between expts
        axes.append(None)
        for j in [3,30]: #rate of invocation
            df_all_runs = None
            for k in [1]: #run number
                test_name = "cs_" + str(k) + "_" + str(j) + "_" + str(i)
                df = func(test_name,j)
                if df_all_runs is None:
                    df_all_runs = df
                else:
                    df_all_runs = pd.concat((df_all_runs, df))
            by_row_index = df_all_runs.groupby(df_all_runs.index)
            df_mean = by_row_index.mean()

            label=str(j)
            if axes[idx] is None:
                axes[idx] = df_mean.plot(y='waitTime',x='invokeTimeRel', label=label)
            else:
                df_mean.plot(y='waitTime',x='invokeTimeRel', label=label, ax=axes[idx])

        img = "plots/wait-time-5thread-" + str(j) + ".png"
        plt.ylabel("Wait Time")
        plt.xlabel("Time Step")
        plt.legend(title="Invocation Rate")
        plt.savefig(img)
        plt.figure()

if __name__== "__main__":
  main()
