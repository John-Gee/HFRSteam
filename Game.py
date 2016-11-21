class Game:
    name  = ""
    appid = ""
    description = ""
    image  = ""
    is_linux = ""
    price = ""
    genres = list()
    release_date = ""
    link = ""
    is_dlc = ""
    available = ""
    avg_review = ""
    cnt_review = ""
    
    def __init__(self, name, appid, description, image, is_linux, price, genres, release_date, link, is_dlc, available, avg_review, cnt_review):
        self.name  = name
        self.appid = appid
        self.description = description
        self.image = image
        self.is_linux = is_linux
        self.price = price
        self.genres = genres
        self.release_date = release_date
        self.link = link
        self.is_dlc = is_dlc
        self.available = available
        self.avg_review = avg_review
        self.cnt_review = cnt_review

    def pretty_print(self):
        print("Name: " + self.name)
        print("AppID: " + self.appid)
        print("Description: " + self.description)
        print("Image: " + self.image)
        print("IsLinux: " + self.is_linux)
        print("Price: " + self.price)
        print("Genres: " + str(self.genres))
        print("Release Date: " + self.release_date)
        print("Link: " + self.link)
        print("IsDLC: " + self.is_dlc)
        print("Available: " + self.available)
        print("Average Review: " + self.avg_review)
        print("Review Count: " + self.cnt_review)
