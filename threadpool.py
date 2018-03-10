import asyncio
from concurrent import futures
import datetime
import logging
import os
import sys
import time
import threading
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


class ThreadPool():
    def create(self, nthreads):
        if (nthreads):
            threads = nthreads
        else:
            threads = get_number_of_cores()
        self.threadpool = futures.ThreadPoolExecutor(threads)


    def shutdown(self, **kwargs):
        logging.debug('shutting down!')
        self.threadpool.shutdown(**kwargs)


    def submit(self, fn, *args):
        return self.threadpool.submit(fn, *args)


threadpool   = ThreadPool()
exceptions   = []
future       = {}
shuttingdown = False
lock         = threading.Lock()
loop         = None

def create(nthreads, lloop):
    global loop
    loop = lloop
    threadpool.create(nthreads)


def shutdown(**kwargs):
    lock.acquire()
    global shuttingdown
    if (not shuttingdown):
        shuttingdown = True
        threadpool.shutdown(**kwargs)
        for calname in future:
            for f in future[calname]:
                f.cancel()
        logging.debug('futures and threadpool stopped')
        loop.call_soon_threadsafe(loop.stop)
        logging.debug('loop stopped')
    lock.release()


def wrap_thread(func, *args):
    try:
        func(*args)
    except Exception as e:
        styledprint.print_error('Exception raised for:', func, e)
        tb = traceback.format_exc()
        if (tb not in exceptions):
            exceptions.append(tb)
            styledprint.print_error(tb)
        # this won't actually end the threadpool
        # until all running threads are done
        shutdown(wait=False)
        raise e


def wait_calname(calname):
    logging.debug('futures.wait() started at: ' + str(datetime.datetime.now().time()))
    logging.debug('len(future[calname]: ' + str(len(future[calname])))
    styledprint.print_info('threadpool tasks:')
    for f in tqdm.tqdm(futures.as_completed(future[calname]), total=len(future[calname])):
        pass
    logging.debug('futures.wait() done at: ' + str(datetime.datetime.now().time()))
    future[calname].clear()
    check_for_errors()


def wait():
    calname = utils.get_caller_name()
    if (calname not in future):
        return
    wait_calname(calname)


def check_for_errors():
    if (len(exceptions)):
        for exception in exceptions:
            styledprint.print_error(exception)
        raise Exception('An exception was raised in some of the threads, see above.')


def submit_job_calname(calname, func, *args):
    if (not len(exceptions)):
        future[calname].append(threadpool.submit(wrap_thread, func, *args))


def submit_job_from(name, func, *args):
    if (name not in future):
        future[name] = []
    submit_job_calname(name, func, *args)


def submit_job(func, *args):
    if (func not in future):
        calname         = utils.get_caller_name()
        future[func]    = calname
    else:
        calname         = future[func]

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
    wait_calname(calname)
