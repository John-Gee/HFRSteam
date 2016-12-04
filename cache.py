import os.path
import pickle
import traceback

_CACHE_FILE = "cache.p"


def retrieve_db_from_cache():
    db = dict()
    try:
        if(os.path.exists(_CACHE_FILE)):
            db = pickle.load(open(_cachefile, "rb"))
    except:
        traceback.print_exc()

    return db


def save_to_cache(db):
    pickle.dump(db, open(_CACHE_FILE, "wb"))


def merge_old_new_cache(db1, db2):

    if ((db1 == None) or (len(db1) == 0)):
        return db2

    if ((db2 == None) or (len(db2) == 0)):
        return db1

    db = dict()
    for key in iter(db1):
        db[key] = db1[key]

    for key in iter(db2):
        db[key] = db2[key]

    return db
