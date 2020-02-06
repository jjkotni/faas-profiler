from mpkmemalloc import *
import multiprocessing as mp
import threading
import psutil
import functools
import gc
import six
import pyperf
import os

from chameleon import PageTemplate


BIGTABLE_ZPT = """\
<table xmlns="http://www.w3.org/1999/xhtml"
xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row python: options['table']">
<td tal:repeat="c python: row.values()">
<span tal:define="d python: c + 1"
tal:attributes="class python: 'column-' + %s(d)"
tal:content="python: d" />
</td>
</tr>
</table>""" % six.text_type.__name__


def main(params):
    runner = pyperf.Runner(loops=1)
    runner.metadata['description'] = "Chameleon template"

    tmpl = PageTemplate(BIGTABLE_ZPT)
    table = [dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)
             for x in range(500)]
    options = {'table': table}

    func = functools.partial(tmpl, options=options)
    runner.bench_func('chameleon', func)

    return({'Result':'Success'})

# if __name__ == '__main__':
#     out = main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {},
#              'activation31':{},'activation33':{},'activation34':{}, 'activation32': {},
#              'activation45':{},'activation46':{},'activation47':{}, 'activation48': {}})

#     process = psutil.Process(os.getpid())
#     print((process.memory_info().rss)/1024)  # in bytes
