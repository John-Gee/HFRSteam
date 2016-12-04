import pickle
import os.path
import traceback

_cachefile="cache.p"

def retrieve_db_from_cache():
    db = dict()
    try:
        if(os.path.exists(_cachefile)):
            db = pickle.load(open(_cachefile, "rb"))
    except:
        traceback.print_exc()

    return db

def save_to_cache(db):
    pickle.dump(db, open(_cachefile, "wb"))

def merge_old_new_cache(db1, db2):
    db = dict()
    for key in iter(db1):
        db[key] = db1[key]
    
    for key in iter(db2):
        db[key] = db2[key]
    
    return db
