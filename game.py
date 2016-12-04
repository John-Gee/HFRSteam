class Game:
    name  = ""
    appid = ""
    description = ""
    image  = ""
    os = list()
    price = 0.00
    price_date = ""
    genres = list()
    release_date = ""
    link = ""
    is_dlc = ""
    available = ""
    avg_review = ""
    cnt_review = ""
    
    def __init__(self, name, appid, description, image, os, price, price_date, genres, release_date, link, is_dlc, available, avg_review, cnt_review):
        self.name  = name
        self.appid = appid
        self.description = description
        self.image = image
        self.os = os
        self.price = price
        self.price_date = price_date
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
        print("OS: " + ", ".join(self.os))
        print("Price: $" + self.price)
        print("Price Date: " + self.price_date)
        print("Genres: " + ", ".join(self.genres))
        print("Release Date: " + self.release_date)
        print("Link: " + self.link)
        print("IsDLC: " + self.is_dlc)
        print("Available: " + self.available)
        print("Average Review: " + self.avg_review)
        print("Review Count: " + self.cnt_review)
