import os.path
import pickle
import traceback


_CACHE_FILE = 'cache/cache.p'


def retrieve_db_from_cache():
    db = dict()
    try:
        if(os.path.exists(_CACHE_FILE)):
            db = pickle.load(open(_CACHE_FILE, 'rb'))
    except:
        traceback.print_exc()

    return db


def save_to_cache(cache):
    pickle.dump(cache, open(_CACHE_FILE, 'wb'))


def merge_old_new_cache(cache1, cache2):
    return {**cache1, **cache2}
