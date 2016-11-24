import JSON
import web
import sys
import stringutils
import os

class SteamDB:
    games = dict()
    
    def __init__(self):
        APPLIST = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
        
        applist = JSON.get_data_from_url(APPLIST)
        for app in iter(applist["applist"]["apps"]["app"]):
            name = app["name"].lower()
            if (name not in self.games):
                self.games[name] = app["appid"]

    def get_appid(self, name):
        cleanname = name.lower()
        if (cleanname in self.games):
            return self.games[cleanname]
        else:
            return ""

    def get_review_from_steam(self, appid):
        URL = "http://store.steampowered.com/app/"
        
        start      = "Aggregaterating"
        real_start = "itemprop=\"description\">"
        end        = "<span class=\"nonresponsive_hidden responsive_reviewdesc\">"
        
        cookie = 'birthtime=568022401'
        page = web.get_utf8_web_page(URL + appid, cookie)
        
        if ("No user reviews" in page):
            return "", "0"
        
        page = stringutils.substringafter(page, start)
        page = stringutils.substringafter(page, real_start)
        page = stringutils.substringbefore(page, end)
        page = page.replace("&nbsp;", os.linesep)
        page = page.replace("<br />", "")
        
        average = stringutils.substringbefore(page, "</span>")
        count   = stringutils.substringafter(page, "<span class=\"responsive_hidden\">")
        count   = stringutils.substringbefore(count, " reviews")
        count   = count.strip().replace("(", "")
        
        return average, count
    
    def get_informatin_from_steamdb(appid):
        return ""
