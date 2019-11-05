import pdb
from PerfMonAnalyzer import ReadPerfMon
import matplotlib.pyplot as plt

def main():
    frames = []
    for j in [1,2]:
        for i in [3, 12, 21, 50, 100, 125]:
            out_file = "logs/cs_" + j + "_" + i + "_90" + "/perf-mon.out"
            df = ReadPerfMon(out_file)
            col_name = i + "(" j + ")"
            df.rename(columns = {'context-switches': col_name},inplace=True)
            frames.append(df)

    plt.savefig('bigRun.png')

if __name__== "__main__":
  main()
