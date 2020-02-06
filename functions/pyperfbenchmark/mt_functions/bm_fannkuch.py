"""
The Computer Language Benchmarks Game
http://benchmarksgame.alioth.debian.org/

Contributed by Sokolov Yura, modified by Tupteq.
"""

import pyperf
from mpkmemalloc import *
import os
import gc
import threading
import psutil
from six.moves import xrange


DEFAULT_ARG = 9


def fannkuch(n):
    count = list(xrange(1, n + 1))
    max_flips = 0
    m = n - 1
    r = n
    check = 0
    perm1 = list(xrange(n))
    perm = list(xrange(n))
    perm1_ins = perm1.insert
    perm1_pop = perm1.pop

    while 1:
        if check < 30:
            check += 1

        while r != 1:
            count[r - 1] = r
            r -= 1

        if perm1[0] != 0 and perm1[m] != m:
            perm = perm1[:]
            flips_count = 0
            k = perm[0]
            while k:
                perm[:k + 1] = perm[k::-1]
                flips_count += 1
                k = perm[0]

            if flips_count > max_flips:
                max_flips = flips_count

        while r != n:
            perm1_ins(r, perm1_pop(0))
            count[r] -= 1
            if count[r] > 0:
                break
            r += 1
        else:
            return max_flips


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    runner = pyperf.Runner(loops=1)
    arg = DEFAULT_ARG
    runner.bench_func('fannkuch', fannkuch, arg)
    del runner
    pymem_reset()

def dummyFunc(name):
    pass

def main(params):
    pymem_setup_allocators(0)
    gc.disable()

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

    pymem_reset_pkru()

    result = {}
    for activation in params:
        result[activation] = "Finished thread execution"

    process = psutil.Process(os.getpid())
    print((process.memory_info().rss)/1024)  # in bytes

    return(result)

if __name__ == '__main__':
    out = main({'activation4':{}, 'activation2': {},
             'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
             'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

    process = psutil.Process(os.getpid())
    print((process.memory_info().rss)/1024)  # in bytes
