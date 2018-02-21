import os.path
import pickle
import traceback


import utils

class Cache():
    def __init__(self, path):
        self.path = path


    def retrieve_db_from_cache(self):
        db = utils.DictCaseInsensitive()
        try:
            if(os.path.exists(self.path)):
                db = pickle.load(open(self.path, 'rb'))
        except:
            traceback.print_exc()
        return db


    def save_to_cache(self, cache):
        pickle.dump(cache, open(self.path, 'wb'))


    def merge_old_new_cache(self, cache1, cache2):
        return {**cache1, **cache2}
