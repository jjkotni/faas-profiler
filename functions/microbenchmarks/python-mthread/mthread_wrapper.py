# Copyright (c) 2019 Princeton University
# Copyright (c) 2014 'Konstantin Makarchev'
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import concurrent.futures
import logging
import threading
import time
import sys
from time import sleep

def functionWorker(params):
    result = { 'output' : 'hello World!'}
    sleep(0.2)    

    print(result)
    
    return result

def main(params):
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    workers = int(params['workers'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(functionWorker, range(workers))


    out    =  'Executed '+str(workers)+' threads'
    result = { 'output': out}

    return(result)

'''
if __name__== "__main__":
  params = {}
  params['workers'] = sys.argv[1]
  print(params)   
  main(params)
'''
