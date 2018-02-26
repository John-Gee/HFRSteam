from concurrent import futures
import os
import sys
import time
import traceback


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


def wrap_thread(threadpool, exceptions, func, arguments):
    try:
        if (not len(exceptions)):
            func(*arguments)
    except:
        print('Exception raised for', func)
        exceptions.append(sys.exc_info())
        # this won't actually end the threadpool
        # until all running threads are done
        threadpool.shutdown(wait=False)

class ThreadPool():
    def __init__(self, nthreads):
        if (nthreads):
            threads = nthreads
        else:
            threads = get_number_of_cores()
        self.threadpool = futures.ThreadPoolExecutor(threads)
        self.exceptions = []
        self.future     = []


    def submit_work(self, func, arguments):
        self.future.append(self.threadpool.submit(wrap_thread, self.threadpool,
                                                  self.exceptions, func,
                                                  arguments))


    def wait(self):
        futures.wait(self.future, timeout=None)
        self.future.clear()
        if (len(self.exceptions)):
            for exception in self.exceptions:
                traceback.print_exception(*exception)
            raise Exception('An exception was raised in some of the threads, see above.')
