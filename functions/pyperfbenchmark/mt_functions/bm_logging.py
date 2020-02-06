"""
Script for testing the performance of logging simple messages.

Rationale for logging_silent by Antoine Pitrou:

"The performance of silent logging calls is actually important for all
applications which have debug() calls in their critical paths.  This is
quite common in network and/or distributed programming where you want to
allow logging many events for diagnosis of unexpected runtime issues
(because many unexpected conditions can appear), but with those logs
disabled by default for performance and readability reasons."

https://mail.python.org/pipermail/speed/2017-May/000576.html
"""

from mpkmemalloc import *
import os
import gc
import threading
import psutil
import pdb
# Python imports
import io
import logging

# Third party imports
import six
from six.moves import xrange
import pyperf

# A simple format for parametered logging
FORMAT = 'important: %s'
MESSAGE = 'some important information to be logged'


def truncate_stream(stream):
    stream.seek(0)
    stream.truncate()


def bench_silent(loops, logger, stream):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    m = MESSAGE
    range_it = xrange(loops)
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)

    dt = pyperf.perf_counter() - t0

    if len(stream.getvalue()) != 0:
        raise ValueError("stream is expected to be empty")

    return dt


def bench_simple_output(loops, logger, stream):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    m = MESSAGE
    range_it = xrange(loops)
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)

    dt = pyperf.perf_counter() - t0

    lines = stream.getvalue().splitlines()
    if len(lines) != loops * 10:
        raise ValueError("wrong number of lines")

    return dt


def bench_formatted_output(loops, logger, stream):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    fmt = FORMAT
    msg = MESSAGE
    range_it = xrange(loops)
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)

    dt = pyperf.perf_counter() - t0

    lines = stream.getvalue().splitlines()
    if len(lines) != loops * 10:
        raise ValueError("wrong number of lines")

    return dt


def add_cmdline_args(cmd, args):
    if args.benchmark:
        cmd.append(args.benchmark)


BENCHMARKS = {
    "silent": bench_silent,
    "simple": bench_simple_output,
    "format": bench_formatted_output,
}


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)

    print("Done with pkey allcoation")

    pdb.set_trace()
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args, loops=1)
    runner.metadata['description'] = "Test the performance of logging."

    # parser = runner.argparser
    # parser.add_argument("benchmark", nargs='?', choices=sorted(BENCHMARKS))

    # options = runner.parse_args()

    # NOTE: StringIO performance will impact the results...
    if six.PY3:
        stream = io.StringIO()
    else:
        stream = io.BytesIO()

    handler = logging.StreamHandler(stream=stream)
    logger = logging.getLogger("benchlogger")
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    # if options.benchmark:
    #     benchmarks = (options.benchmark,)
    # else:
    #     benchmarks = sorted(BENCHMARKS)
    benchmarks = sorted(BENCHMARKS)

    for bench in benchmarks:
        name = 'logging_%s' % bench
        bench_func = BENCHMARKS[bench]

        print("Running bench")
        runner.bench_time_func(name, bench_func,
                               logger, stream,
                               inner_loops=10)
    print("Passed this")
    del runner
    pymem_reset()

def dummyFunc(loops, name):
    pass

def main(params):
    pymem_setup_allocators(0)
    gc.disable()

    workers = len(params) if (len(params)>0) else 1

    runner  = pyperf.Runner(loops = 1)

    runner.argparser.add_argument("--cases")

    stream = io.StringIO()
    handler = logging.StreamHandler(stream=stream)
    logger = logging.getLogger("benchlogger")
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    runner.bench_time_func("Dummy init", bench_silent, logger, stream, inner_loops=10)

    del runner

    threads = []
    for i in range(workers):
        tname = 'Worker' + str(i)
        threads.append(threading.Thread(target=functionWorker, args=[tname,1], name=tname))

    for idx, thread in enumerate(threads):
        print("executing worker idx: ", str(idx))
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
    out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
             'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
             'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

    process = psutil.Process(os.getpid())
    print((process.memory_info().rss)/1024)  # in bytes
