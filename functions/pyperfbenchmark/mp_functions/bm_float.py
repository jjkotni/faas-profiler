"""
Artificial, floating point-heavy benchmark originally used by Factor.
"""
from six.moves import xrange
import multiprocessing as mp
from mpkmemalloc import *
import os
import gc
import threading
import psutil
import pyperf

from math import sin, cos, sqrt


POINTS = 100000


class Point(object):
    __slots__ = ('x', 'y', 'z')

    def __init__(self, i):
        self.x = x = sin(i)
        self.y = cos(i) * 3
        self.z = (x * x) / 2

    def __repr__(self):
        return "<Point: x=%s, y=%s, z=%s>" % (self.x, self.y, self.z)

    def normalize(self):
        x = self.x
        y = self.y
        z = self.z
        norm = sqrt(x * x + y * y + z * z)
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def maximize(self, other):
        self.x = self.x if self.x > other.x else other.x
        self.y = self.y if self.y > other.y else other.y
        self.z = self.z if self.z > other.z else other.z
        return self


def maximize(points):
    next = points[0]
    for p in points[1:]:
        next = next.maximize(p)
    return next


def benchmark(n):
    points = [None] * n
    for i in xrange(n):
        points[i] = Point(i)
    for p in points:
        p.normalize()
    return maximize(points)


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    runner = pyperf.Runner(loops=1)
    runner.metadata['description'] = "Float benchmark"
    points = POINTS
    runner.bench_func('float', benchmark, points)
    del runner
    pymem_reset()

    process = psutil.Process(os.getpid())
    print((process.memory_full_info().pss)/1024.0)  # in bytes

def dummyFunc(name):
    pass

def main(params):
    # pymem_setup_allocators(0)
    gc.disable()

    workers = len(params) if (len(params)>0) else 1

    runner  = pyperf.Runner(loops = 1)

    runner.argparser.add_argument("--cases")

    runner.bench_func("Dummy init", dummyFunc, "main")

    del runner

    threads = []
    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(mp.Process(target=functionWorker, args=[tname,0], name=tname))

    for idx, thread in enumerate(threads):
        thread.start()
        thread.join()

    pymem_reset_pkru()

    result = {}
    for activation in params:
        result[activation] = "Finished thread execution"

    process = psutil.Process(os.getpid())
    print((process.memory_full_info().pss)/1024.0)  # in bytes

    return(result)

if __name__ == '__main__':
    out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
             'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
             'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})