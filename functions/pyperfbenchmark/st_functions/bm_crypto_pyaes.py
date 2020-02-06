#!/usr/bin/env python
"""
Pure-Python Implementation of the AES block-cipher.

Benchmark AES in CTR mode using the pyaes module.
"""

from mpkmemalloc import *
import multiprocessing as mp
import os
import gc
import threading
import psutil
import pyperf
from six.moves import xrange

import pyaes

# 23,000 bytes
CLEARTEXT = b"This is a test. What could possibly go wrong? " * 500

# 128-bit key (16 bytes)
KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'


def bench_pyaes(loops):
    range_it = xrange(loops)
    t0 = pyperf.perf_counter()

    for loops in range_it:
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(CLEARTEXT)

        # need to reset IV for decryption
        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)

        # explicitly destroy the pyaes object
        aes = None

    dt = pyperf.perf_counter() - t0
    if plaintext != CLEARTEXT:
        raise Exception("decrypt error!")

    return dt

def main(params):
    runner = pyperf.Runner(loops=1)
    runner.metadata['description'] = ("Pure-Python Implementation "
                                      "of the AES block-cipher")
    runner.bench_time_func('crypto_pyaes', bench_pyaes)

    return({'Result':'Success'})

# if __name__ == '__main__':
#     out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
#              'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
#              'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

#     process = psutil.Process(os.getpid())
#     print((process.memory_info().rss)/1024)  # in bytes
