import asyncio
from concurrent import futures
from datetime import datetime
import logging
import os
import sys
import time
import tqdm
import traceback

import styledprint
import utils


def get_number_of_cores():
    if (sys.platform.startswith('linux')):
        cores = len(os.sched_getaffinity(0))
        if (cores):
            return cores
    if (sys.platform.startswith('win32')):
        if (os.environ.get("NUMBER_OF_PROCESSORS")):
            cores = int(os.environ["NUMBER_OF_PROCESSORS"])
            if (cores):
                return cores
    return 1


class Pool():
    def create(self, ncpus):
        if (not ncpus):
            ncpus  = get_number_of_cores()
        self.ncpus = ncpus
        self.pool  = futures.ProcessPoolExecutor(self.ncpus)


    def shutdown(self, **kwargs):
        logging.debug('shutting down!')
        self.pool.shutdown(**kwargs)


    def submit(self, fn, *args):
        return self.pool.submit(fn, *args)


pool         = Pool()
exceptions   = []
future       = {}
shuttingdown = False
loop         = None


def create_pool(ncpus, lloop):
    global loop
    loop = lloop
    pool.create(ncpus)


def shutdown_pool(**kwargs):
    global shuttingdown
    if (not shuttingdown):
        shuttingdown = True
        pool.shutdown(**kwargs)
        for calname in future:
            for f in future[calname]:
                f.cancel()
        logging.debug('futures and pool stopped')
        if (len(exceptions)):
            loop.call_soon_threadsafe(loop.stop)
            logging.debug('loop stopped')


def wrap_task(func, *args):
    try:
        return func(*args)
    except Exception as e:
        styledprint.print_error('Exception raised for:', func, e)
        tb = traceback.format_exc()
        if (tb not in exceptions):
            exceptions.append(tb)
            styledprint.print_error(tb)
        raise e


def check_task(f):
    if (f.exception()):
        # this won't actually end the pool
        # until all running tasks are done
        shutdown_pool(wait=False)


def wait_calname(calname):
    if (calname not in future):
        return []

    logging.debug('futures.wait() started at: ' + str(datetime.now().time()))
    logging.debug('len(future[calname]: ' + str(len(future[calname])))
    styledprint.print_info('pool tasks:')
    for f in tqdm.tqdm(futures.as_completed(future[calname]), total=len(future[calname])):
        pass
    logging.debug('futures.wait() done at: ' + str(datetime.now().time()))
    fs = future[calname]
    del future[calname]
    return fs


def wait():
    calname = utils.get_caller_name()
    return wait_calname(calname)


def check_for_errors():
    if (len(exceptions)):
        for exception in exceptions:
            styledprint.print_error(exception)
        raise Exception('An exception was raised in some of the parallel tasks, see above.')


def submit_job_calname(calname, func, *args):
    if (not len(exceptions)):
        f = pool.submit(wrap_task, func, *args)
        f.add_done_callback(check_task)
        future[calname].append(f)


def submit_job_from(name, func, *args):
    if (name not in future):
        future[name] = []
    return submit_job_calname(name, func, *args)


def submit_job(func, *args):
    calname = utils.get_caller_name()
    submit_job_from(calname, func, *args)


def submit_jobs(args):
    calname         = utils.get_caller_name()
    future[calname] = []
    while True:
        try:
            arg  = next(args)
            submit_job_calname(calname, *arg)
        except StopIteration:
            break
    return wait_calname(calname)


def split_submit_job(dict1, dict2, func, *args):
    calname = utils.get_caller_name()
    curCPU  = 0
    subDict = [utils.DictCaseInsensitive() for x in range(pool.ncpus)]

    for key in dict1:
        subDict[curCPU][key] = dict1[key]
        curCPU+=1
        if (curCPU == pool.ncpus):
            curCPU = 0

    future[calname] = []
    for i in range(pool.ncpus):
        submit_job_calname(calname, func, subDict[i], *args)

    fs = wait_calname(calname)


    for f in fs:
        subDict = f.result()
        for key in subDict:
            dict2[key] = subDict[key]
