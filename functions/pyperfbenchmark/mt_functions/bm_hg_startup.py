import sys
import subprocess

from mpkmemalloc import *
import os
import gc
import threading
import psutil
import pyperf
from pyperformance.venv import get_venv_program


def get_hg_version(hg_bin):
    # Fast-path: use directly the Python module
    try:
        from mercurial.__version__ import version
        if sys.version_info >= (3,) and isinstance(version, bytes):
            return version.decode('utf8')
        else:
            return version
    except ImportError:
        pass

    # Slow-path: run the "hg --version" command
    proc = subprocess.Popen([sys.executable, hg_bin, "--version"],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    stdout = proc.communicate()[0]
    if proc.returncode:
        print("ERROR: Mercurial command failed!")
        sys.exit(proc.returncode)
    return stdout.splitlines()[0]


# if __name__ == "__main__":
def functionWorker(tname, allocate_pkey):
    if allocate_pkey:
        pkey_thread_mapper(tname)
    runner = pyperf.Runner(values=25, loops=1)

    runner.metadata['description'] = "Performance of the Python startup"
    args = runner.parse_args()

    hg_bin = get_venv_program('hg')
    runner.metadata['hg_version'] = get_hg_version(hg_bin)

    command = [sys.executable, hg_bin, "help"]
    runner.bench_command('hg_startup', command)
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
