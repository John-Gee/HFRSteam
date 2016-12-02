import sys
import os
import Game
import SteamDB
import JSON
import time
import datetime
import calendar
import traceback
import urllib
import re
import cache
import stringutils
import Mapper

def getshortdescription(longdesc):
    if (longdesc == None):
        return longdesc
    
    MAXLENGTH = 400
    
    cleandesc = longdesc.replace("\"", "").replace(os.linesep, " ").replace("\r", " ")
    cleandesc = re.sub("<br.?.?>", " ", cleandesc)
    cleandesc = re.sub("<.*?>", "", cleandesc)
    cleandesc = re.sub(" +", " ", cleandesc)
    
    if (len(cleandesc) > MAXLENGTH):
        shortdesc = stringutils.rsubstringbefore(cleandesc[:MAXLENGTH], " ") + " [...]"
        return shortdesc
    
    return cleandesc
    
def parse_list(names_list, options):
    APPDETAIL="http://store.steampowered.com/api/appdetails?appids="
    if (options.ignorecache):
        cachedgames = dict()
    else:
        cachedgames = cache.retrieve_db_from_cache()
    
    if (options.cacheonly):
        return cachedgames
    
    steamDB = SteamDB.SteamDB()
    mapper = Mapper.Mapper()
    games = dict()
    i = 0
    
    keys = list(steamDB.get_list_of_games())

    for name in iter(names_list):
        BEGINSTRIKED = "<strike><span style=\"color:#FF0000\">"
        ENDSTRIKED   = "</span></strike>"
        cleanname = name.strip()
        if (cleanname.startswith(BEGINSTRIKED) or cleanname.endswith(ENDSTRIKED)):
            cleanname = cleanname.replace(BEGINSTRIKED, "")
            cleanname = cleanname.replace(ENDSTRIKED, "")
            available = "no"
        else:
            available = "yes"
        if(cleanname.startswith("(+)")):
            cleanname = cleanname[3:]
            is_dlc = "true"
        else:
            is_dlc = "false"

        cleanname= re.sub("<.*?>", "", cleanname)
        
        cleanname = cleanname.strip()
        
        if (cleanname == ""):
            continue

        if (available == "yes"):
            
            #Allow to break for dev purposes
            i += 1
            if ( (options.number_games != None) and (options.number_games.isdigit()) and (i == int(options.number_games)) ):
                break
            
            if ( (cleanname in cachedgames) and (cachedgames[cleanname].appid != "") and (not options.refreshall) and ( (options.game == None) or (options.game.lower() not in cleanname.lower())) ):
                games[cleanname] = cachedgames[cleanname]
            else:
                appid = ""
                description = ""
                image = ""
                os = list()
                price = None
                price_date = ""
                genres = list()
                release_date = ""
                link = ""
                avg_review = ""
                cnt_review = ""
                
                mappedname = mapper.get_mapping(cleanname)
                if (mappedname == None):
                    appid = str(steamDB.get_appid(cleanname))

                    if (appid == ""):
                        res = mapper.get_match(cleanname.lower(), keys)
                        if(len(res) > 0):
                            appid = str(steamDB.get_appid(res[0]))
                            if (appid != ""):
                                mapper.add_to_mapping(cleanname, res[0])
                                print("Matched " + cleanname + " with " + res[0])

                elif (mappedname != "NA"):
                    appid = str(steamDB.get_appid(mappedname))

                if (appid == ""):
                    print("The game " + name + " was not found in the steam db.")
                    description = "The game was not found in the steam db."
                else:
                    try:
                        info = JSON.get_data_from_url(APPDETAIL + appid)
                        if ("data" in info[appid]) and (len(info[appid]["data"]) > 0):
                            
                            if (len(info[appid]["data"]["short_description"]) > 0):
                                description = getshortdescription(info[appid]["data"]["short_description"])
                            elif (len(info[appid]["data"]["about_the_game"]) > 0):
                                description = getshortdescription(info[appid]["data"]["about_the_game"])
                            else:
                                description = getshortdescription(info[appid]["data"]["detailed_description"])
                            
                            image = info[appid]["data"]["header_image"]
                            
                            if ( ("type" in info[appid]["data"]) and (info[appid]["data"]["type"].lower() == "dlc") ):
                                is_dlc = "true"

                            if (len(info[appid]["data"]["linux_requirements"]) > 0):
                                os.append("Linux")
                            if (len(info[appid]["data"]["mac_requirements"]) > 0):
                                os.append("Mac")
                            if (len(info[appid]["data"]["pc_requirements"]) > 0):
                                os.append("Windows")
                            
                            if (info[appid]["data"]["is_free"]):
                                price = 0.00
                            elif ( ("price_overview" in info[appid]["data"]) and (len(info[appid]["data"]["price_overview"]) > 0)):
                                price = (info[appid]["data"]["price_overview"]["final"]) / 100
                            elif ( (len(info[appid]["data"]["package_groups"]) > 0) and (info[appid]["data"]["package_groups"][0]["subs"][0]["price_in_cents_with_discount"] >= 0) ):
                                price = (info[appid]["data"]["package_groups"][0]["subs"][0]["price_in_cents_with_discount"]) / 100
                            else:
                                price = None

                            if ( (price != None) and (price > 60) ):
                                print("The price of game " + cleanname + ": " + price + " is suspicious.")
                            
                            price_date = str(datetime.datetime.now().date())
                            price_date = calendar.month_abbr[int(price_date[5:7])] + " " + price_date[8:] + ", " + price_date[:4]

                            if ("genres" in info[appid]["data"]):
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
                            if(options.waitonsteamtimeout):
                                sleep(1000)
                            else:
                                break
                    except:
                        print("something failed for game: " + cleanname + " appid: " + appid + ", " + str(datetime.datetime.now().time()))
                        traceback.print_exc()
                    time.sleep(2)
                game = Game.Game(cleanname, appid, description, image, os, price, price_date, genres, release_date, link, is_dlc, available, avg_review, cnt_review)
                games[cleanname] = game

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    mapper.save_mapping()
    return games
