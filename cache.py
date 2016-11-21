import pickle
import os.path
import traceback

cachefile="cache.p"

def retrieve_db_from_cache():
    db = dict()
    try:
        if(os.path.exists(cachefile)):
            db = pickle.load(open(cachefile, "rb"))
    except:
        traceback.print_exc()
    return db

def save_to_cache(db):
    pickle.dump(db, open(cachefile, "wb"))
