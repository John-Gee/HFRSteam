import JSON
import web
import sys
import stringutils
import os

APPLIST = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
_games = dict()    
_applist = JSON.get_data_from_url(APPLIST)
for app in iter(_applist["applist"]["apps"]["app"]):
    name = app["name"].lower()
    if (name not in _games):
        _games[name] = app["appid"]

def get_appid(name):
    cleanname = name.lower()
    if (cleanname in _games):
        return _games[cleanname]
    else:
        return ""

def get_appinfo(appid):
    APPDETAIL="http://store.steampowered.com/api/appdetails?appids="

    return JSON.get_data_from_url(APPDETAIL + appid)

def get_review_from_steam(appid):
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

def get_list_of_games():
    return _games.keys()
