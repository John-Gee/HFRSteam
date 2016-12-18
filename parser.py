import os
import re
import sys
import time
import pdb

import cache
from game import Game
from mapper import Mapper
import steam
import stringutils


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
    i                   = 0

    keys = list(steam.get_list_of_games())

    for name in iter(names_list):
        BEGIN_STRIKED = "<strike><span style=\"color:#FF0000\">"
        END_STRIKED   = "</span></strike>"
        cleanname     = name.strip()
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

        cleanname = re.sub("<.*?>", "", cleanname)

        cleanname = cleanname.strip()

        if ((cleanname == "") or (available == "no")):
            continue

        # Allow to break for dev purposes
        i += 1
        if ((options.number_games != None) and (options.number_games.isdigit()) and (i == int(options.number_games))):
            break

        if ((cleanname in cachedgames) and (cachedgames[cleanname].appid) and (not options.refreshall) and ((options.game == None) or (options.game.lower() not in cleanname.lower()))):
            games[cleanname]           = cachedgames[cleanname]
            games[cleanname].available = available

        else:
            appid        = appidsmapping.get_mapping(cleanname)
            mappedname   = namesmapping.get_mapping(cleanname)

            if (appid == None):
                if (mappedname == None):
                    appid = str(steam.get_appid(cleanname))
                    if(options.matchingwords):
                        if (appid == ""):
                            matchednames = Mapper.get_match(
                                cleanname.lower(), keys)
                            if(len(matchednames) > 0):
                                appid = str(steam.get_appid(matchednames[0]))
                                if (appid != ""):
                                    namesmapping.add_to_mapping(
                                        cleanname, matchednames[0])
                                    print("Matched " + cleanname +
                                          " with " + matchednames[0])

                elif (mappedname != "NA"):
                    appid = str(steam.get_appid(mappedname))
            else:
                print("appid mapping found for game " + cleanname)

            game           = Game(cleanname)
            game.appid     = appid
            game.is_dlc    = is_dlc
            game.available = available

            if ((appid == None) or (appid == "")):
                game.appid = ""
                game.description = "The game was not found in the steam db."
                print("The game " + name + " " + game.description)

            else:
                steam.get_game_info(game)

            games[cleanname] = game

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    appidsmapping.save_mapping()
    namesmapping.save_mapping()
    return games
