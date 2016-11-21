import sys
import Game
import SteamDB
import JSON
import time
import datetime
import traceback
import urllib
import cache
import stringutils

def getshortdescription(longdesc):
    return stringutils.substringbefore(longdesc, "<")

def parse_list(names_list):
    APPDETAIL="http://store.steampowered.com/api/appdetails?appids="
    steamDB = SteamDB.SteamDB()
    games = cache.retrieve_db_from_cache()
    for name in iter(names_list):
        BEGINSTRIKED = "<strike><span style=\"color:#FF0000\">"
        ENDSTRIKED   = "</span></strike>"
        cleanname = name.rstrip().lstrip()
        if (cleanname.startswith(BEGINSTRIKED) or cleanname.endswith(ENDSTRIKED)):
            cleanname = cleanname.replace(BEGINSTRIKED, "")
            cleanname = cleanname.replace(ENDSTRIKED, "")
            available = "no"
        else:
            available = "yes"
        if(cleanname.startswith("(+)")):
            cleanname = cleanname[3:]
            is_dlc = "yes"
        else:
            is_dlc = "no"
        if (available == "yes") and ((cleanname not in games) or (games[cleanname].appid == "")):
            appid = str(steamDB.get_appid(cleanname))
            description = ""
            image = ""
            is_linux = ""
            price = ""
            genres = list()
            release_date = ""
            link = ""
            avg_review = ""
            cnt_review = ""
            
            if (appid == ""):
                print("The game " + cleanname + " was not found in the steam db.")
                description = "The game was not found in the steam db."
            else:
                try:
                    avg_review, cnt_review = steamDB.get_review_from_steam(appid)
                    info = JSON.get_data_from_url(APPDETAIL + appid)
                    if ("data" in info[appid]) and (len(info[appid]["data"]) > 0):
                        if (len(info[appid]["data"]["short_description"]) > 0):
                            description = getshortdescription(info[appid]["data"]["short_description"])
                        else:
                            description = getshortdescription(info[appid]["data"]["about_the_game"])
                        image = "\"" + info[appid]["data"]["header_image"] + "\""
                        if (len(info[appid]["data"]["linux_requirements"]) > 0):
                            is_linux = "yes"
                        else:
                            is_linux = "no"
                        if ( ("price_overview" in info[appid]["data"]) and (len(info[appid]["data"]["price_overview"]) > 0)):
                            price = "$" + str((info[appid]["data"]["price_overview"]["final"]) / 100)
                        else:
                            price = "$0.00"
                        for genre in iter (info[appid]["data"]["genres"]):
                            genres.append(genre["description"])
                        release_date = info[appid]["data"]["release_date"]["date"]
                        link = "http://store.steampowered.com/app/" + appid
                        avg_review, cnt_review = steamDB.get_review_from_steam(appid)
                        print("Info for game " + cleanname + " was retrieved" + ", " + str(datetime.datetime.now().time()))
                    else:
                        description = "The game is not on steam anymore"
                except urllib.error.HTTPError as err:
                    
                    if (repr(err).find("302")):
                        description = "The game is in the db but not on steam anymore"
                    else:
                        print("We're temp banned from steam no point in continuing.")
                        #sleep(1000)
                        break
                except:
                    print("something failed for game: " + cleanname + " appid: " + appid + ", " + str(datetime.datetime.now().time()))
                    traceback.print_exc()
                time.sleep(2)
            game = Game.Game(cleanname, appid, description, image, is_linux, price, genres, release_date, link, is_dlc, available, avg_review, cnt_review)
            games[cleanname] = game

    cache.save_to_cache(games)
    return games
