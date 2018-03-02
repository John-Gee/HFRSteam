import datetime
import os
import sys
import traceback

from cache import Cache
import threadpool
from game import Category
from game import StoreData
from mapper import Mapper
import namematching
import steam
import styledprint
import utils


def get_appid_and_type(name, games):
    if (name in games):
        return games[name]
    else:
        return None, None


def get_game_info(options, game, cachedgames, steamgames,
                  cleansteamgames, name, urlsmapping):
    if ((not options.all) and (not game.hfr.is_available)):
        # Ignoring not available games for now
        # it may be better in the future to ignore them in output
        # or allow the user to do so in the html page.
        return

    # Whether the cache is ignored or not,
    # if a game cached has a gift_date we keep it
    if ((name in cachedgames) and (cachedgames[name].hfr.gift_date)):
        game.hfr.gift_date = cachedgames[name].hfr.gift_date

    if ((name in cachedgames) and (cachedgames[name].store.link)
        and (not options.ignorecache)
        and ((not options.game)
                or (options.game.lower() not in name.lower()))):

        game.store         = cachedgames[name].store

    elif (not options.cacheonly):
        mapping = urlsmapping.get_mapping(name)

        if (mapping == None):
            namestried  = []
            appidstried = []
            while (True):
                appid, typ = get_appid_and_type(name, steamgames)
                if ((not options.nofuzzymatching) and (not appid)):
                    cleanname = namematching.nameclean(name)
                    appid, typ = get_appid_and_type(cleanname, cleansteamgames)
                    if (not appid):
                        matchedname = namematching.get_match(cleanname,
                                                             cleansteamgames.keys(),
                                                             namestried, 0.92)
                        if (matchedname):
                            appid, typ = get_appid_and_type(matchedname,
                                                            cleansteamgames)
                            score = namematching.get_match_score(cleanname.lower(),
                                                                 matchedname.lower())
                            print('Matched {0} with {1} at score {2}'
                                  .format(name, matchedname, score))
                            namestried.append(matchedname)

                if ( (appid in appidstried) or (not appid)):
                    game.store = StoreData()
                    game.store.description = 'The game was not found in the steam db'
                    styledprint.print_error('{0}: {1}'
                                            .format(game.store.description, name))
                    return
                else:
                    appidstried.append(appid)

                    if (steam.get_store_info_from_appid(game, name, appid, typ)):
                        break

        else:
            url      = mapping[0]

            if (url == 'ignore'):
                styledprint.print_info('{0} cannot be found and is to be ignored'
                                       .format(name))
                return

            styledprint.print_info('URL mapping found for game {0}'
                                   .format(name))
            steam.get_store_info_from_url(game, name, url)
            # overwriting the steam provided category
            if (len(mapping) == 2):
                game.store.category = Category[mapping[1].upper()]
                game.store.override = True

        styledprint.print_info('Info for game {0} was retrieved, {1}'
                               .format(name,
                                       str(datetime.datetime.now().time())))


def get_games_info(options, games, steamgames):
    styledprint.print_info_begin('Pulling games information')
    CACHE_PATH      = os.path.join('cache', 'games.p')
    cache           = Cache(CACHE_PATH)
    cachedgames     = cache.load_from_cache()
    cleansteamgames = utils.DictCaseInsensitive()
    for game in steamgames:
        cleansteamgames[namematching.nameclean(game)] = steamgames[game]

    URLS_MAPPING  = os.path.join('mappings', 'urlsmapping.txt')
    urlsmapping   = Mapper(URLS_MAPPING)

    threadpool.submit_jobs(((get_game_info, options, games[name], cachedgames,
                              steamgames, cleansteamgames, name, urlsmapping)
                             for name in games))

    if (not options.dryrun):
        newcachedgames = cache.merge_old_new_cache(cachedgames, games)
        cache.save_to_cache(newcachedgames)
        urlsmapping.save_mapping()

    styledprint.print_info_end('Pulling games information')
