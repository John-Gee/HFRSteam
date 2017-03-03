class HFRData:
    def __init__(self):
        self.is_available = True
        self.is_new       = False


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
        self.is_dlc       = False
        self.avg_review   = ''
        self.cnt_review   = ''
        self.tags         = list()
        self.details      = list()


class Game:
    def __init__(self):
        self.hfr          = HFRData()
        self.store        = StoreData()
