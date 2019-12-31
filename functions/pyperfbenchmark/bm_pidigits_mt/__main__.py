# coding: utf-8
"""
Calculating some of the digits of π.

This benchmark stresses big integer arithmetic.

Adapted from code on:
http://benchmarksgame.alioth.debian.org/
"""

import itertools

from six.moves import map as imap
import pyperf
import threading
from mpkmemalloc import *

DEFAULT_DIGITS = 2000
icount = itertools.count
islice = itertools.islice


def gen_x():
    return imap(lambda k: (k, 4 * k + 2, 0, 2 * k + 1), icount(1))


def compose(a, b):
    aq, ar, as_, at = a
    bq, br, bs, bt = b
    return (aq * bq,
            aq * br + ar * bt,
            as_ * bq + at * bs,
            as_ * br + at * bt)


def extract(z, j):
    q, r, s, t = z
    return (q * j + r) // (s * j + t)


def gen_pi_digits():
    z = (1, 0, 0, 1)
    x = gen_x()
    while 1:
        y = extract(z, 3)
        while y != extract(z, 4):
            z = compose(z, next(x))
            y = extract(z, 3)
        z = compose((10, -10 * y, 0, 1), z)
        yield y


def calc_ndigits(n):
    return list(islice(gen_pi_digits(), n))


def add_cmdline_args(cmd, args):
    cmd.extend(("--digits", str(args.digits)))


def functionWorker(runner, tid, digits, tname):
    pymem_set_pkru(tname)
    bmk_name = 'pidigits_' + str(tid)
    runner.bench_func(bmk_name, calc_ndigits, digits)

def main(params):
    pymem_setup_allocators()
    workers = params['workers'] if ('workers' in params) else 1
    runner  = pyperf.Runner(loops = 1)
    threads = []

    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(threading.Thread(target=functionWorker, 
                                        args=[runner,i, DEFAULT_DIGITS, tname], 
                                        name=tname))
    
    for idx, thread in enumerate(threads):
        pkey_thread_mapper(thread.name)
        thread.start()
        thread.join()
    pymem_set_pkru(thread.name)

    result = {}

    for activation in params:
        result[activation] = "Finished thread execution"

    return(result)
    
#if __name__ == '__main__':
#    main({'workers':2})
