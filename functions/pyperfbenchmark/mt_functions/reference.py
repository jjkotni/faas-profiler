from mpkmemalloc import *
import pdb
import json
import sys
import threading
import pyperf
import six
from six.moves import xrange
import tracemalloc
import gc
import os
import psutil
import time

EMPTY = ({}, 2000)
SIMPLE_DATA = {'key1': 0, 'key2': True, 'key3': 'value', 'key4': 'foo',
               'key5': 'string'}
SIMPLE = (SIMPLE_DATA, 1000)
NESTED_DATA = {'key1': 0, 'key2': SIMPLE[0], 'key3': 'value', 'key4': SIMPLE[0],
               'key5': SIMPLE[0], six.u('key'): six.u('\u0105\u0107\u017c')}
NESTED = (NESTED_DATA, 1000)
HUGE = ([NESTED[0]] * 1000, 1)

CASES = ['EMPTY', 'SIMPLE', 'NESTED', 'HUGE']

def bench_json_dumps(data):
    for obj, count_it in data:
        for _ in count_it:
            json.dumps(obj)

def add_cmdline_args(cmd, args):
    if args.cases:
        cmd.extend(("--cases", args.cases))

def functionWorker(tid, tname, allocate_pkey):
    runner  = pyperf.Runner(add_cmdline_args=add_cmdline_args, loops = 1)

    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                      % ', '.join(CASES))

    if allocate_pkey:
        pkey_thread_mapper(tname)

    cases = CASES
    data = []
    for case in cases:
        obj, count = globals()[case]
        data.append((obj, xrange(count)))

    func_name = 'json_dumps_' + str(tid)
    runner.bench_func(func_name, bench_json_dumps, data)
    del runner
    runner = None
    pymem_reset()

def dummyFunc(name):
    pass

def main(params):
    pymem_setup_allocators(0)

    workers = len(params) if (len(params)>0) else 1

    runner  = pyperf.Runner(add_cmdline_args=add_cmdline_args, loops = 1)

    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                      % ', '.join(CASES))

    runner.bench_func("Dummy init", dummyFunc, "main")

    del runner

    threads = []
    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(threading.Thread(target=functionWorker, args=[i, tname,1], name=tname))

    for idx, thread in enumerate(threads):
        thread.start()
        thread.join()

    pymem_reset_pkru()

    result = {}
    for activation in params:
        result[activation] = "Finished thread execution"

    return(result)

# if __name__ == '__main__':
#      gc.disable()
#      out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
#                  'activation11':{},'activation13':{},'activation14':{}, 'activation12': {},
#                  'activation21':{},'activation23':{},'activation24':{}, 'activation22': {},
#                  'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
#                  'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

#      process = psutil.Process(os.getpid())
#      print((process.memory_info().rss)/1024)  # in bytes
