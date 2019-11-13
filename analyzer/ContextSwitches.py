import pdb
from PerfMonAnalyzer import ReadPerfMon
import matplotlib.pyplot as plt
import pandas as pd
import pdb

from WorkloadChecker import CheckWorkloadValidity

def main():
    axes =[]
    plt.figure()
#    for i in [20, 45, 60, 120]: #gap between expts
#        for j in [3,6, 9, 12, 15, 18, 21, 24, 27, 30, 40, 50, 75, 100, 125 ]: #rate of invocation
    for idx, i in enumerate([20, 45, 60, 120]): #gap between expts
        axes.append(None)
        for j in [6, 9, 18, 30, 75, 125]: #rate of invocation
            df_all_runs = None
            for k in [1, 2, 3, 4, 5]: #run number
                out_file = "logs/cs_" + str(k) + "_" + str(j) + "_" + str(i) + "/perf-mon.out"
                df = ReadPerfMon(out_file)
                if df_all_runs is None:
                    df_all_runs = df
                else:
                    df_all_runs = pd.concat((df_all_runs, df))
            by_row_index = df_all_runs.groupby(df_all_runs.index)
            df_mean = by_row_index.mean()

            label=str(j)
            if axes[idx] is None:
                axes[idx] = df_mean.plot(y='context-switches', label=label)
            else:
                df_mean.plot(y='context-switches', label=label, ax=axes[idx])

        img = "plots/context-switches-5thread-" + str(i) + ".png"
        plt.ylabel("Context Switches")
        plt.xlabel("Time Step")
        plt.legend(title="Invocation Rate")
        plt.savefig(img)
        plt.figure()

if __name__== "__main__":
    pdb.set_trace()
    main()