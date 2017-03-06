from concurrent.futures import ThreadPoolExecutor
import os
import re
import sys
import time
import traceback

import cache
from game import Category, Game
from mapper import Mapper
import steam


_exc_infos = list()


def get_game_info(threadpool, options, games, cachedgames, keys, gameName,
                  urlsmapping, namesmapping):
    global _exc_infos

    try:
        if (len(_exc_infos)):
            return

        game = games[gameName]
        if ((options.all == None) and (not game.hfr.is_available)):
            # Ignoring not available games for now
            # it may be better in the future to ignore them in output
            # or allow the user to do so in the html page.
            return

        if ((gameName in cachedgames) and (cachedgames[gameName].store.link)
            and (not options.refreshall)
            and ((options.game == None)
                 or (options.game.lower() not in gameName.lower()))):

            # TODO only cache steam-related data
            game.store     = cachedgames[gameName].store

        else:
            url          = urlsmapping.get_mapping(gameName)
            mappedname   = namesmapping.get_mapping(gameName)

            if (url == None):
                if (mappedname == None):
                    appid = str(steam.get_appid(gameName))
                    if ((options.matchingwords) and (appid == '')):
                        matchednames = Mapper.get_match(gameName.lower(), keys)
                        if(len(matchednames) > 0):
                            appid = str(steam.get_appid(matchednames[0]))
                            if (appid != ''):
                                namesmapping.add_to_mapping(
                                    gameName, matchednames[0])
                                print('Matched {0} with {1}'.
                                        format(gameName, matchednames[0]))
                elif (mappedname != 'NA'):
                    appid = str(steam.get_appid(mappedname))
                else:
                    appid = None

                if ((appid == None) or (appid == '')):
                    game.store.appid = ''
                    game.store.description = 'The game was not found in the steam db.'
                    print('The game {0} was not found in the steam db.'.format(gameName))
                else:
                    steam.get_store_info_from_appid(game, gameName, appid)

            else:
                print('url mapping found for game {0}'.format(gameName))
                steam.get_store_info_from_url(game, gameName, url)

    except:
        _exc_infos.append(sys.exc_info())
        threadpool.shutdown(wait=False)


def get_games_info(options, games):

    if (options.ignorecache):
        cachedgames = dict()
    else:
        cachedgames = cache.retrieve_db_from_cache()

    if (options.cacheonly):
        return cachedgames

    MAPPING_FOLDER     = 'mappings'
    URLS_MAPPING_FILE  = MAPPING_FOLDER + '/urlsmapping.txt'
    NAMES_MAPPING_FILE = MAPPING_FOLDER + '/namesmapping.txt'
    urlsmapping        = Mapper(URLS_MAPPING_FILE)
    namesmapping       = Mapper(NAMES_MAPPING_FILE)

    keys               = list(steam.get_list_of_games())

    threadpool         = ThreadPoolExecutor(options.threads)

    i                  = 0

    global _exc_infos

    for gameName in iter(games):
        # Allow to break for dev purposes
        i += 1
        if ((options.number_games != None) and (options.number_games.isdigit())
            and (i == int(options.number_games))):
            break

        if (len(_exc_infos)):
            break

        threadpool.submit(get_game_info, threadpool,
                          options, games, cachedgames, keys, gameName, urlsmapping,
                          namesmapping)

    threadpool.shutdown(wait=True)
    if (len(_exc_infos)):
        for exc_info in _exc_infos:
            traceback.print_exception(*exc_info)
        raise Exception('An exception was raised in some of the threads, see above.')

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    urlsmapping.save_mapping()
    namesmapping.save_mapping()
