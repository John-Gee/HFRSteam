class HFRData:
    def __init__(self, is_available, is_new):
        self.is_available = is_available
        self.is_new       = is_new


class StoreData:
    def __init__(self):
        self.appid        = ''
        self.description  = ''
        self.image        = ''
        self.os           = list()
        self.price        = None
        self.price_date   = ''
        self.genres       = list()
        self.release_date = ''
        self.link         = ''
        self.category     = ''
        self.avg_review   = ''
        self.cnt_review   = ''
        self.tags         = list()
        self.details      = list()


class Game:
    def __init__(self, is_available, is_new):
        self.hfr          = HFRData(is_available, is_new)
        self.store        = StoreData()
