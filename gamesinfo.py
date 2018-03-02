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


def get_appid_and_type(name, games, appidstried):
    if (name in games):
        for app in games[name]:
            if (app[0] not in appidstried):
                return app
    return None, None


def get_appid_and_type_from_namematching(origname, name, games, appidstried,
                                         namestried, lastmatch):
    while (True):
        if ((not lastmatch[-1]) or (lastmatch[-1] in namestried)):
            matchedname = namematching.get_match(name, games.keys(),
                                                 namestried, 0.92)
        else:
            matchedname = lastmatch[-1]
        if (matchedname):
            score         = namematching.get_match_score(name, matchedname)
            lastmatch[-1] = matchedname
            print('Matched {0} with {1} at score {2}'
                  .format(origname, matchedname, score))
            appid, typ    = get_appid_and_type(matchedname, games, appidstried)
            if (appid):
                return appid, typ
            else:
                namestried.append(matchedname)
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
            appidstried = []
            namestried  = []
            lastmatch   = ['']
            while (True):
                appid, typ = get_appid_and_type(name, steamgames, appidstried)
                if (appid):
                    styledprint.print_debug('The game {0} got its appid simply'
                                            .format(name))
                elif (not options.nofuzzymatching):
                    cleanname = namematching.nameclean(name)
                    appid, typ = get_appid_and_type(cleanname, cleansteamgames,
                                                    appidstried)
                    if (appid):
                        styledprint.print_debug('The game {0} got its appid '
                                                'by namecleaning'
                                                .format(name))
                    else:
                        appid, typ = get_appid_and_type_from_namematching(name,
                                                                          cleanname,
                                                                          cleansteamgames,
                                                                          appidstried,
                                                                          namestried,
                                                                          lastmatch)

                if ((appid in appidstried) or (not appid)):
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
