from concurrent import futures
import os
import sys
import time
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
        return self.threadpool.shutdown(**kwargs)


    def submit(self, fn, *args):
        return self.threadpool.submit(fn, *args)


threadpool = ThreadPool()
exceptions = []
future     = {}


def create(nthreads):
    threadpool.create(nthreads)


def wrap_thread(func, *args):
    try:
        if (not len(exceptions)):
            func(*args)
    except:
        styledprint.print_error('Exception raised for:', func)
        exceptions.append(sys.exc_info())
        # this won't actually end the threadpool
        # until all running threads are done
        threadpool.shutdown(wait=False)


def submit_work(func, *args):
    if (func not in future):
        calname         = utils.get_caller_name()
        future[func]    = calname
    else:
        calname         = future[func]
    if (calname not in future):
        future[calname] = []

    future[calname].append(threadpool.submit(wrap_thread, func, *args))


def wait():
    calname = utils.get_caller_name()
    if (calname not in future):
        return

    futures.wait(future[calname], timeout=None)
    future[calname].clear()
    if (len(exceptions)):
        for exception in exceptions:
            traceback.print_exception(*exception)
        raise Exception('An exception was raised in some of the threads, see above.')
