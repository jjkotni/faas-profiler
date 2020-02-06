from mpkmemalloc import *
import multiprocessing as mp
import threading
import glob
import os.path
import sys
import psutil
import pyperf

# if __name__ == "__main__":
def main(params):
    runner = pyperf.Runner(loops=1)

    runner.metadata['description'] = "Performance of the Python 2to3 program"
    args = runner.parse_args()

    datadir = os.path.join(os.path.dirname(__file__), 'data', '2to3')
    pyfiles = glob.glob(os.path.join(datadir, '*.py.txt'))

    command = [sys.executable, "-m", "lib2to3", "-f", "all"] + pyfiles

    runner.bench_command('2to3', command)

    process = psutil.Process(os.getpid())
    print(process.memory_full_info())  # in bytes
    return({'output':'Success'})

# if __name__ == '__main__':
#     out = main({'activation1':{}})

#     process = psutil.Process(os.getpid())
#     print((process.memory_info().rss)/1024)  # in bytes
