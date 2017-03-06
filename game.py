from enum import Enum, auto


class Category(Enum):
    Game       = auto()
    DLC        = auto()
    Collection = auto()


class HFRData:
    def __init__(self, is_available, is_new):
        self.is_available = is_available
        self.is_new       = is_new


class StoreData:
    def __init__(self):
        self.description  = ''
        self.image        = ''
        self.os           = list()
        self.price        = None
        self.price_date   = ''
        self.genres       = list()
        self.release_date = ''
        self.link         = ''
        self.category     = None
        self.avg_review   = ''
        self.cnt_review   = ''
        self.tags         = list()
        self.details      = list()


class Game:
    def __init__(self, is_available, is_new):
        self.hfr          = HFRData(is_available, is_new)
        self.store        = StoreData()


    # we're only interested in pickling the store member
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['hfr']
        return state


    # unpickle the state, which should only be the store member
    def __setstate__(self, state):
        self.__dict__.update(state)
