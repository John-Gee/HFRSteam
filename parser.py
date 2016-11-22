import sys
import Game
import SteamDB
import JSON
import time
import datetime
import calendar
import traceback
import urllib
import cache
import stringutils
import Mapper

def getshortdescription(longdesc):
    return stringutils.substringbefore(longdesc, "<")

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
            
        mappedname = mapper.get_mapping(cleanname)
        if (mappedname != None):
            cleanname = mappedname
            
        if (available == "yes"):
            
            #Allow to break for dev purposes
            i += 1
            if ( (options.number_games != None) and (options.number_games.isdigit()) and (i == int(options.number_games)) ):
                break
            
            if ( (cleanname in cachedgames) and (cachedgames[cleanname].appid != "") and (not options.refreshall) and ( (options.game == None) or (options.game.lower() not in cleanname.lower())) ):
                games[cleanname] = cachedgames[cleanname]
            else:
                appid = str(steamDB.get_appid(cleanname))
                j = 0
                tolookfor= ["(", "+"]
                while ( (appid == "") and (j < len(tolookfor)) ):
                    cleanname2 = stringutils.substringbefore(cleanname, tolookfor[j]).strip()
                    j += 1
                    appid = str(steamDB.get_appid(cleanname2))
                    if (appid != ""):
                        mapper.add_to_mapping(cleanname, cleanname2)
                        cleanname = cleanname2
                        break
                
                description = ""
                image = ""
                os = list()
                price = ""
                price_date = ""
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
                        info = JSON.get_data_from_url(APPDETAIL + appid)
                        if ("data" in info[appid]) and (len(info[appid]["data"]) > 0):
                            
                            if (len(info[appid]["data"]["short_description"]) > 0):
                                description = getshortdescription(info[appid]["data"]["short_description"])
                            else:
                                description = getshortdescription(info[appid]["data"]["about_the_game"])
                            if (description != None):
                                description = description.replace("\"", "")
                            
                            image = info[appid]["data"]["header_image"]
                            
                            if (len(info[appid]["data"]["linux_requirements"]) > 0):
                                os.append("Linux")
                            if (len(info[appid]["data"]["mac_requirements"]) > 0):
                                os.append("Mac")
                            if (len(info[appid]["data"]["pc_requirements"]) > 0):
                                os.append("Windows")
                                
                            if ( ("price_overview" in info[appid]["data"]) and (len(info[appid]["data"]["price_overview"]) > 0)):
                                price = "$" + str((info[appid]["data"]["price_overview"]["final"]) / 100)
                            else:
                                price = "$0.00"
                            price_date = str(datetime.datetime.now().date())
                            price_date = calendar.month_abbr[int(price_date[5:7])] + " " + price_date[8:] + ", " + price_date[:4]

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
