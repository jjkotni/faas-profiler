import pdb
import json
import sys
import concurrent.futures
import logging
import threading
import pyperf
import six
from six.moves import xrange


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


def main():
    pdb.set_trace()
    '''
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args)
    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                       % ', '.join(CASES))
    runner.metadata['description'] = "Benchmark json.dumps()"

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
    '''
    cases = CASES

    data = []
    for case in cases:
        obj, count = globals()[case]
        data.append((obj, xrange(count)))

    runner.bench_func('json_dumps', bench_json_dumps, data)

'''
def main(params):
    pdb.set_trace()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    workers = int(params['workers'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(functionWorker, range(workers))


    out    =  'Executed '+str(workers)+' threads'
    result = { 'output': out}

    return(result)

#if __name__ == '__main__':
#    params = {}
#    params['workers'] = 1
#    main(params)