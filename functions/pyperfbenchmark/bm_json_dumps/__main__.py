import pdb
import json
import sys
import threading
import pyperf
import six
from six.moves import xrange
from mpkmemalloc import *
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

def functionWorker(runner, tid, tname):
    # print("Tname passed in worker is ", tname)
    pymem_set_pkru(tname)
    args = runner.parse_args()
    if args.cases:
        cases = []
        for case in args.cases.split(','):
            case = case.strip()
            if case:
                cases.append(case)
        if not cases:
            print("ERROR: empty list of cases")
            sys.exit(1)
    else:
        cases = CASES

    data = []
    for case in cases:
        obj, count = globals()[case]
        data.append((obj, xrange(count)))

    func_name = 'json_dumps_' + str(tid)
    runner.bench_func(func_name, bench_json_dumps, data)
    #pymem_reset_pkru()

def main(params):
    tracemalloc.start()
    pymem_setup_allocators()

    workers = len(params) if (len(params)>0) else 1

    print("Identified ", str(workers), " workers")
    workers = 5

    runner  = pyperf.Runner(add_cmdline_args=add_cmdline_args, loops = 1)

    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                      % ', '.join(CASES))
    threads = []
    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(threading.Thread(target=functionWorker, args=[runner,i, tname], name=tname))

    for idx, thread in enumerate(threads):
        # print("Executing ", thread.name)
        pkey_thread_mapper(thread.name)
        thread.start()
        thread.join()
        # print("Finished executing ", thread.name)
    pymem_set_pkru(thread.name)

    result = {}
    for activation in params:
        result[activation] = "Finished thread execution"

    process = psutil.Process(os.getpid())
    print((process.memory_info().rss)/1024)  # in bytes

    return(result)

#if __name__ == '__main__':
    #tracemalloc.start()
    #main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {}})
    #snapshot = tracemalloc.take_snapshot()
    #process = psutil.Process(os.getpid())
    #print((process.memory_info().rss)/1024)  # in bytes
    #top_stats = snapshot.statistics('lineno')

# print("[ Top 10  ]")
# for stat in top_stats[:10]:
#     print(stat)
