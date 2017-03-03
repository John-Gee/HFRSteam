class Game:


    def __init__(self, name):
        self.name         = name
        self.appid        = ''
        self.description  = ''
        self.image        = ''
        self.os           = list()
        self.price        = None
        self.price_date   = ''
        self.genres       = list()
        self.release_date = ''
        self.link         = ''
        self.is_dlc       = ''
        self.avg_review   = ''
        self.cnt_review   = ''
        self.tags         = list()
        self.details      = list()
        self.available    = True
        self.is_new       = False
