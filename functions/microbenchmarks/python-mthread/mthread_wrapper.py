# Copyright (c) 2019 Princeton University
# Copyright (c) 2014 'Konstantin Makarchev'
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import concurrent.futures
import logging
import threading
import time

def functionWorker(params):
    result = { 'output' : 'hello World!'}

    print(result)
    
    return result

def main(params):
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(functionWorker, range(15))

    result = { 'output': 'Executed 15 threads'}

    return(result)
