from enum import Enum, auto


import utils


class Category(Enum):
    Game       = auto()
    DLC        = auto()
    Collection = auto()


class HFRData(utils.ComparableClass):
    def __init__(self, is_available, requirements, is_new, gift_date):
        self.is_available = is_available
        self.requirements = requirements
        self.is_new       = is_new
        self.gift_date    = gift_date


class StoreData(utils.ComparableClass):
    def __init__(self):
        self.description  = ''
        self.image        = ''
        self.os           = list()
        self.price        = None
        self.price_date   = ''
        self.genres       = list()
        self.release_date = None
        self.link         = ''
        self.category     = None
        self.avg_review   = None
        self.cnt_review   = None
        self.tags         = list()
        self.details      = list()
        self.override     = False
        self.languages    = list()


class Game(utils.ComparableClass):
    def __init__(self, is_available=False, requirements=None,
                 is_new=False, gift_date=None):
        self.hfr          = HFRData(is_available, requirements,
                                    is_new, gift_date)
        self.store        = StoreData()

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
