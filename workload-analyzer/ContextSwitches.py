import pdb
from PerfMonAnalyzer import ReadPerfMon
from tkinter import * 

def main():
    perfDataFrame = ReadPerfMon("stats/cs/roi/10.out")
    pdb.set_trace()

if __name__== "__main__":
  main()
