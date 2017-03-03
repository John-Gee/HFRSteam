from concurrent.futures import ThreadPoolExecutor
import os
import re
import sys
import time
import traceback

import cache
from game import Game
from mapper import Mapper
import steam
import stringutils


_exc_infos = list()


def get_game_info(threadpool, options, games, cachedgames, keys, name,
                  appidsmapping, namesmapping, i, numberofnewgames):
    global _exc_infos

    try:
        if (len(_exc_infos)):
            return

        BEGIN_STRIKED = '<strike><span style=color:#FF0000>'
        END_STRIKED   = '</span></strike>'
        cleanname     = name.strip()

        if (cleanname.startswith(BEGIN_STRIKED) or cleanname.endswith(END_STRIKED)):
            cleanname = cleanname.replace(BEGIN_STRIKED, '')
            cleanname = cleanname.replace(END_STRIKED, '')
            available = False
        else:
            available = True

        if(cleanname.startswith('(+)')):
            cleanname = cleanname[3:]
            is_dlc = True
        else:
            is_dlc = False

        cleanname = re.sub('<.*?>', '', cleanname)

        cleanname = cleanname.strip()

        if (not cleanname):
            print('The cleanname is empty for game {0}!'.format(name))
            return
        
        is_new = True if (i <= numberofnewgames) else False

        if ((options.all == None) and (not available)):
            # Ignoring not available games for now
            # it may be better in the future to ignore them in output
            # or allow the user to do so in the html page.
            return


        if ((cleanname in cachedgames) and (cachedgames[cleanname].appid) and (not options.refreshall) and ((options.game == None) or (options.game.lower() not in cleanname.lower()))):

            # TODO only cache steam-related data
            games[cleanname]           = cachedgames[cleanname]
            games[cleanname].available = available
            games[cleanname].is_new    = is_new

        else:
            appid        = appidsmapping.get_mapping(cleanname)
            mappedname   = namesmapping.get_mapping(cleanname)

            if (appid == None):
                if (mappedname == None):
                    appid = str(steam.get_appid(cleanname))
                    if(options.matchingwords):
                        if (appid == ''):
                            matchednames = Mapper.get_match(
                                cleanname.lower(), keys)
                            if(len(matchednames) > 0):
                                appid = str(steam.get_appid(matchednames[0]))
                                if (appid != ''):
                                    namesmapping.add_to_mapping(
                                        cleanname, matchednames[0])
                                    print('Matched {0} with {1}'.
                                          format(cleanname, matchednames[0]))

                elif (mappedname != 'NA'):
                    appid = str(steam.get_appid(mappedname))
            else:
                print('appid mapping found for game {0}'.format(cleanname))

            game           = Game(cleanname)
            game.appid     = appid
            game.is_dlc    = is_dlc
            game.available = available
            game.is_new    = is_new

            if ((appid == None) or (appid == '')):
                game.appid = ''
                game.description = 'The game was not found in the steam db.'
                print('The game {0} was not found in the steam db.'.format(cleanname))

            else:
                steam.get_game_info(game)

            games[cleanname] = game
    except:
        _exc_infos.append(sys.exc_info())
        threadpool.shutdown(wait=False)


def parse_list(options, names_list, numberofnewgames=0):

    if (options.ignorecache):
        cachedgames = dict()
    else:
        cachedgames = cache.retrieve_db_from_cache()

    if (options.cacheonly):
        return cachedgames

    games               = dict()

    MAPPING_FOLDER      = 'mappings'
    APPIDS_MAPPING_FILE = MAPPING_FOLDER + '/appidsmapping.txt'
    NAMES_MAPPING_FILE  = MAPPING_FOLDER + '/namesmapping.txt'
    appidsmapping       = Mapper(APPIDS_MAPPING_FILE)
    namesmapping        = Mapper(NAMES_MAPPING_FILE)

    keys                = list(steam.get_list_of_games())

    threadpool          = ThreadPoolExecutor(options.threads)

    i                   = 0

    global _exc_infos

    for name in iter(names_list):
        # Allow to break for dev purposes
        i += 1
        if ((options.number_games != None) and (options.number_games.isdigit()) and (i == int(options.number_games))):
            break

        if (len(_exc_infos)):
            break

        threadpool.submit(get_game_info, threadpool,
                          options, games, cachedgames, keys, name, appidsmapping, namesmapping, i, numberofnewgames)

    threadpool.shutdown(wait=True)
    if (len(_exc_infos)):
        for exc_info in _exc_infos:
            traceback.print_exception(*exc_info)
        raise Exception('An exception was raised in some of the threads, see above.')

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    appidsmapping.save_mapping()
    namesmapping.save_mapping()
    return games
