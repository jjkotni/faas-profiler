"""
Render a template using Genshi module.
"""

import pyperf
from mpkmemalloc import *
import os
import gc
import threading
import psutil
from six.moves import xrange

from genshi.template import MarkupTemplate, NewTextTemplate


BIGTABLE_XML = """\
<table xmlns:py="http://genshi.edgewall.org/">
<tr py:for="row in table">
<td py:for="c in row.values()" py:content="c"/>
</tr>
</table>
"""

BIGTABLE_TEXT = """\
<table>
{% for row in table %}<tr>
{% for c in row.values() %}<td>$c</td>{% end %}
</tr>{% end %}
</table>
"""


def bench_genshi(loops, tmpl_cls, tmpl_str):
    tmpl = tmpl_cls(tmpl_str)
    table = [dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)
             for _ in range(1000)]
    range_it = xrange(loops)
    t0 = pyperf.perf_counter()

    for _ in range_it:
        stream = tmpl.generate(table=table)
        stream.render()

    return pyperf.perf_counter() - t0


def add_cmdline_args(cmd, args):
    if args.benchmark:
        cmd.append(args.benchmark)


BENCHMARKS = {
    'xml': (MarkupTemplate, BIGTABLE_XML),
    'text': (NewTextTemplate, BIGTABLE_TEXT),
}


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args, loops =1)
    runner.metadata['description'] = "Render a template using Genshi module"
    runner.argparser.add_argument("benchmark", nargs='?',
                                  choices=sorted(BENCHMARKS))

    args = runner.parse_args()
    if args.benchmark:
        benchmarks = (args.benchmark,)
    else:
        benchmarks = sorted(BENCHMARKS)

    for bench in benchmarks:
        name = 'genshi_%s' % bench
        tmpl_cls, tmpl_str = BENCHMARKS[bench]
        runner.bench_time_func(name, bench_genshi, tmpl_cls, tmpl_str)
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
    out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
             'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
             'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

    process = psutil.Process(os.getpid())
    print((process.memory_info().rss)/1024)  # in bytes
