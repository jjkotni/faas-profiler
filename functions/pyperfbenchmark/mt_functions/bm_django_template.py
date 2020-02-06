"""Test the performance of the Django template system.

This will have Django generate a 150x150-cell HTML table.
"""

from six.moves import xrange
from mpkmemalloc import *
import os
import gc
import threading
import psutil
import pyperf

import django.conf
from django.template import Context, Template


# 2016-10-10: Python 3.6 takes 380 ms
DEFAULT_SIZE = 100


def bench_django_template(runner, size):
    template = Template("""<table>
{% for row in table %}
<tr>{% for col in row %}<td>{{ col|escape }}</td>{% endfor %}</tr>
{% endfor %}
</table>
    """)
    table = [xrange(size) for _ in xrange(size)]
    context = Context({"table": table})

    runner.bench_func('django_template', template.render, context)


def prepare_cmd(runner, cmd):
    cmd.append("--table-size=%s" % runner.args.table_size)


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    # django.conf.settings.configure(TEMPLATES=[{
    #     'BACKEND': 'django.template.backends.django.DjangoTemplates',
    # }])
    # django.setup()

    runner = pyperf.Runner(loops=1)
    cmd = runner.argparser
    cmd.add_argument("--table-size",
                     type=int, default=DEFAULT_SIZE,
                     help="Size of the HTML table, height and width "
                          "(default: %s)" % DEFAULT_SIZE)

    args = runner.parse_args()
    runner.metadata['description'] = "Django template"
    runner.metadata['django_version'] = django.__version__
    runner.metadata['django_table_size'] = args.table_size

    bench_django_template(runner, args.table_size)
    del runner
    pymem_reset()

def dummyFunc(name):
    pass

def main(params):
    pymem_setup_allocators(0)
    gc.disable()

    workers = len(params) if (len(params)>0) else 1

    # functionWorker("main", 0)
    django.conf.settings.configure(TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
    }])
    django.setup()
    runner  = pyperf.Runner(loops = 1)
    bench_django_template(runner, DEFAULT_SIZE)
    del runner

    threads = []
    for i in range(workers):
        print("executing thread: ", str(i))
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
