import os.path
import pickle
import traceback


_CACHE_FILE = 'cache.p'


def retrieve_db_from_cache():
    db = dict()
    try:
        if(os.path.exists(_CACHE_FILE)):
            db = pickle.load(open(_CACHE_FILE, 'rb'))
    except:
        traceback.print_exc()

    return db


def save_to_cache(db):
    pickle.dump(db, open(_CACHE_FILE, 'wb'))


def merge_old_new_cache(ignore_cache, db1, db2):
    for game in db2:
        if (game in db1) and (db1[game].hfr.gift_date is not None):
            db2[game].hfr.gift_date = db1[game].hfr.gift_date
    if ignore_cache:
        return db2
    else:
        return {**db1, **db2}

