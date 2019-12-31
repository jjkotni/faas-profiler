import subprocess 
#import os
#import psutil 
#import tracemalloc
import sys

def main(params):
    workers = int(params['workers'])
    cmd = "python3.6 "+ params['script'] + " -l 1"
    #cmd = [ "python3.6", sys.argv[2], "-l 1"]

    for worker in range(workers):
        #p = subprocess.Popen(cmd)
        p = subprocess.run([cmd], shell=True)
        #print("Subprocess pid: ", str(p.pid))
        #sprocess = psutil.Process(p.pid)
        #print("Sub process: ", str(p.pid), "Memory(in KB): ", (sprocess.memory_info().rss)/1024)  # in bytes

    return({'output': 'Finished'})

if __name__ == '__main__':
    #tracemalloc.start()
    #main({'activation1':{},'activation3':{},'activation4':{}, 'activation2': {}})
    #snapshot = tracemalloc.take_snapshot()
    #process = psutil.Process(os.getpid())
    #print((process.memory_info().rss)/1024)  # in bytes
    #top_stats = snapshot.statistics('lineno')
    out = main({'workers': sys.argv[1], 'script': sys.argv[2]})
    #print(out)
