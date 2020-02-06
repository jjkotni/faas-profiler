"""Wrapper script for testing the performance of the html5lib HTML 5 parser.

The input data is the spec document for HTML 5, written in HTML 5.
The spec was pulled from http://svn.whatwg.org/webapps/index.
"""
from __future__ import with_statement

from mpkmemalloc import *
import os
import gc
import threading
import psutil
import io
import os.path

import html5lib
import pyperf
import six


__author__ = "collinwinter@google.com (Collin Winter)"


def bench_html5lib(html_file):
    html_file.seek(0)
    html5lib.parse(html_file)


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    runner = pyperf.Runner(loops=1)
    runner.metadata['description'] = (
        "Test the performance of the html5lib parser.")
    runner.metadata['html5lib_version'] = html5lib.__version__

    # Get all our IO over with early.
    filename = os.path.join(os.path.dirname(__file__),
                            "data", "w3_tr_html5.html")
    with io.open(filename, "rb") as fp:
        html_file = six.BytesIO(fp.read())

    runner.bench_func('html5lib', bench_html5lib, html_file)
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

# if __name__ == '__main__':
#     out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
#              'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
#              'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

#     process = psutil.Process(os.getpid())
#     print((process.memory_info().rss)/1024)  # in bytes
