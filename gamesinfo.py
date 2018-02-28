import datetime
import os
import sys
import traceback

from cache import Cache
import threadpool
from game import Category
from mapper import Mapper
import namematching
import steam
import styledprint
import utils


def get_appid(name, games):
    cleanname = name
    if (cleanname in games):
        return str(games[cleanname])
    else:
        return None


def get_namematching(name, steamgames):
    matchedname = namematching.get_match(name, steamgames.keys())
    if (matchedname):
        appid = get_appid(matchedname, steamgames)
        if (appid != ''):
            urlsmapping.add_to_mapping(name,
                                        steam.get_urlmapping_from_appid(appid))
            styledprint.print_info('Matched {0} with {1}'
                                   .format(name, matchedname))


def get_game_info(options, game, cachedgames, steamgames, name, urlsmapping):
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
        mapping  = urlsmapping.get_mapping(name)

        if (mapping == None):
            appid = get_appid(name, steamgames)
            if ((options.matchingwords) and (not appid)):
                matchedname = get_namematching(name, steamgames)

            if (not appid):
                game.store.appid = ''
                game.store.description = 'The game was not found in the steam db'
                styledprint.print_error('{0}: {1}'
                                       .format(game.store.description, name))
                return
            else:
                steam.get_store_info_from_appid(game, name, appid)

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
    CACHE_PATH    = os.path.join('cache', 'games.p')
    cache         = Cache(CACHE_PATH)
    cachedgames   = utils.DictCaseInsensitive(cache.load_from_cache())

    URLS_MAPPING  = os.path.join('mappings', 'urlsmapping.txt')
    urlsmapping   = Mapper(URLS_MAPPING)

    threadpool.submit_jobs(((get_game_info, options, games[name],
                              cachedgames, steamgames, name, urlsmapping)
                             for name in games))

    if (not options.dryrun):
        newcachedgames = cache.merge_old_new_cache(cachedgames, games)
        cache.save_to_cache(newcachedgames)
        urlsmapping.save_mapping()

    styledprint.print_info_end('Pulling games information')
