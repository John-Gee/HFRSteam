import calendar
import datetime
import os
import re
import sys
import time
import traceback
import urllib
import pdb

import cache
from game import Game
from mapper import Mapper
import steamdb
import stringutils

def getshortdescription(longdesc):
    if (longdesc == None):
        return longdesc
    
    MAX_LENGTH = 400
    
    cleandesc = longdesc.replace("\"", "").replace(os.linesep, " ").replace("\r", " ")
    cleandesc = re.sub("<br.?.?>", " ", cleandesc)
    cleandesc = re.sub("<.*?>", "", cleandesc)
    cleandesc = re.sub(" +", " ", cleandesc)
    
    if (len(cleandesc) > MAX_LENGTH):
        shortdesc = stringutils.rsubstringbefore(cleandesc[:MAX_LENGTH], " ") + " [...]"
        return shortdesc
    
    return cleandesc
    
def parse_list(names_list, options):
    if (options.ignorecache):
        cachedgames = dict()
    else:
        cachedgames = cache.retrieve_db_from_cache()
    
    if (options.cacheonly):
        return cachedgames
    
    games = dict()
    MAPPING_FOLDER      = "mappings"
    APPIDS_MAPPING_FILE = MAPPING_FOLDER + "/" + "appidsmapping.txt"
    NAMES_MAPPING_FILE  = MAPPING_FOLDER + "/" + "namesmapping.txt"
    appidsmapping       = Mapper(APPIDS_MAPPING_FILE)
    namesmapping        = Mapper(NAMES_MAPPING_FILE)
    i     = 0
    
    keys = list(steamdb.get_list_of_games())

    for name in iter(names_list):
        BEGIN_STRIKED = "<strike><span style=\"color:#FF0000\">"
        END_STRIKED   = "</span></strike>"
        cleanname = name.strip()
        if (cleanname.startswith(BEGIN_STRIKED) or cleanname.endswith(END_STRIKED)):
            cleanname = cleanname.replace(BEGIN_STRIKED, "")
            cleanname = cleanname.replace(END_STRIKED, "")
            available = "no"
        else:
            available = "yes"

        if(cleanname.startswith("(+)")):
            cleanname = cleanname[3:]
            is_dlc = "1"
        else:
            is_dlc = "0"

        cleanname= re.sub("<.*?>", "", cleanname)
        
        cleanname = cleanname.strip()
        
        if ((cleanname == "") or (available == "no")):
            continue

        #Allow to break for dev purposes
        i += 1
        if ( (options.number_games != None) and (options.number_games.isdigit()) and (i == int(options.number_games)) ):
            break
        
        if ((cleanname in cachedgames) and (cachedgames[cleanname].appid != "") and (not options.refreshall) and ( (options.game == None) or (options.game.lower() not in cleanname.lower()))):
            games[cleanname] = cachedgames[cleanname]

        else:
            description  = ""
            image        = ""
            os           = list()
            price        = None
            price_date   = ""
            genres       = list()
            release_date = ""
            link         = ""
            avg_review   = ""
            cnt_review   = ""
            
            appid        = appidsmapping.get_mapping(cleanname)
            mappedname   = namesmapping.get_mapping(cleanname)
            
            if (appid  == None):
                if (mappedname == None):
                    appid = str(steamdb.get_appid(cleanname))
                    if (appid == ""):
                        matchednames = Mapper.get_match(cleanname.lower(), keys)
                        if(len(matchednames) > 0):
                            appid = str(steamdb.get_appid(matchednames[0]))
                            if (appid != ""):
                                namesmapping.add_to_mapping(cleanname, matchednames[0])
                                print("Matched " + cleanname + " with " + matchednames[0])

                elif (mappedname != "NA"):
                    appid = str(steamdb.get_appid(mappedname))

            if ((appid == None) or (appid == "")):
                appid = ""
                print("The game " + name + " was not found in the steam db.")
                description = "The game was not found in the steam db."

            else:
                try:
                    avg_review, cnt_review = steamdb.get_review_from_steam(appid)
                    
                    info = steamdb.get_appinfo(appid)
                    if ("data" in info[appid]) and (len(info[appid]["data"]) > 0):
                        
                        if (len(info[appid]["data"]["short_description"]) > 0):
                            description = getshortdescription(info[appid]["data"]["short_description"])
                        elif (len(info[appid]["data"]["about_the_game"]) > 0):
                            description = getshortdescription(info[appid]["data"]["about_the_game"])
                        else:
                            description = getshortdescription(info[appid]["data"]["detailed_description"])
                        
                        image = info[appid]["data"]["header_image"]
                        
                        if ( ("type" in info[appid]["data"]) and (info[appid]["data"]["type"].lower() == "dlc") ):
                            is_dlc = "1"

                        if (len(info[appid]["data"]["linux_requirements"]) > 0):
                            os.append("Linux")
                        if (len(info[appid]["data"]["mac_requirements"]) > 0):
                            os.append("Mac")
                        if (len(info[appid]["data"]["pc_requirements"]) > 0):
                            os.append("Windows")
                        
                        if (info[appid]["data"]["is_free"]):
                            price = 0.00
                        elif (("price_overview" in info[appid]["data"]) and (len(info[appid]["data"]["price_overview"]) > 0)):
                            price = (info[appid]["data"]["price_overview"]["final"]) / 100
                        elif ((len(info[appid]["data"]["package_groups"]) > 0) and (info[appid]["data"]["package_groups"][0]["subs"][0]["price_in_cents_with_discount"] >= 0)):
                            price = (info[appid]["data"]["package_groups"][0]["subs"][0]["price_in_cents_with_discount"]) / 100
                        else:
                            price = None

                        if ((price != None) and (price > 60)):
                            print("The price of game " + cleanname + ": " + price + " is suspicious.")
                        
                        price_date = str(datetime.datetime.now().date())
                        price_date = calendar.month_abbr[int(price_date[5:7])] + " " + price_date[8:] + ", " + price_date[:4]

                        if ("genres" in info[appid]["data"]):
                            for genre in iter (info[appid]["data"]["genres"]):
                                genres.append(genre["description"])
                            
                        release_date = info[appid]["data"]["release_date"]["date"]
                        
                        link = "http://store.steampowered.com/app/" + appid
                        
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

            game = Game(cleanname, appid, description, image, os, price, price_date, genres, release_date, link, is_dlc, available, avg_review, cnt_review)
            games[cleanname] = game

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    appidsmapping.save_mapping()
    namesmapping.save_mapping()
    return games
