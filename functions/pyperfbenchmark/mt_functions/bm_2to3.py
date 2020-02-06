from mpkmemalloc import *
import threading
import glob
import os.path
import sys

import pyperf

# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)

    runner = pyperf.Runner()

    runner.metadata['description'] = "Performance of the Python 2to3 program"
    args = runner.parse_args()

    datadir = os.path.join(os.path.dirname(__file__), 'data', '2to3')
    pyfiles = glob.glob(os.path.join(datadir, '*.py.txt'))

    command = [sys.executable, "-m", "lib2to3", "-f", "all"] + pyfiles

    runner.bench_command('2to3', command)

    del runner
    pymem_reset()

def dummyFunc(name):
    pass

def main(params):
    pymem_setup_allocators(0)

    workers = len(params) if (len(params)>0) else 1

    runner  = pyperf.Runner(loops = 1)

    runner.argparser.add_argument("--cases")

    runner.bench_func("Dummy init", dummyFunc, "main")

    del runner

    threads = []
    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(threading.Thread(target=functionWorker, args=[tname,1], name=tname))

    for idx, thread in enumerate(threads):
        thread.start()
        thread.join()

    result = {}
    for activation in params:
        result[activation] = "Finished thread execution"

    return(result)

# if __name__ == '__main__':
#      gc.disable()
#      out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
#                  'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
#                  'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

#      process = psutil.Process(os.getpid())
#      print((process.memory_info().rss)/1024)  # in bytes
