from concurrent.futures import ThreadPoolExecutor
import datetime
import os
import sys
import traceback

from cache import Cache
import cpu
from game import Category
from mapper import Mapper
import namematching
import steam


_exc_infos = list()


def get_namematching(name, steamgames):
    matchedname = namematching.get_match(name, steamgames)
    if (matchedname):
        appid = steam.get_appid(matchedname)
        if (appid != ''):
            urlsmapping.add_to_mapping(name,
                                        steam.get_urlmapping_from_appid(appid))
            print('Matched {0} with {1}'.format(name, matchedname))


def get_game_info(threadpool, options, game, cachedgames, steamgames, name,
                  urlsmapping):
    global _exc_infos

    try:
        if (len(_exc_infos)):
            return

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
                appid = steam.get_appid(name)
                if ((options.matchingwords) and (not appid)):
                    matchedname = get_namematching(name, steamgames)

                if (not appid):
                    game.store.appid = ''
                    game.store.description = 'The game was not found in the steam db.'
                    print('The game {0} was not found in the steam db.'.format(name))
                    return
                else:
                    steam.get_store_info_from_appid(game, name, appid)

            else:
                url      = mapping[0]

                if (url == 'ignore'):
                    print ('{0} cannot be found and is to be ignored'.format(name))
                    return

                print('URL mapping found for game {0}'.format(name))
                steam.get_store_info_from_url(game, name, url)
                # overwriting the steam provided category
                if (len(mapping) == 2):
                    game.store.category = Category[mapping[1].upper()]
                    game.store.override = True

            print('Info for game {0} was retrieved, {1}'
                  .format(name, str(datetime.datetime.now().time())))

    except:
        print('Exception raised for app {0}'.format(name))
        _exc_infos.append(sys.exc_info())
        threadpool.shutdown(wait=False)


def get_games_info(options, games):
    CACHE_PATH    = os.path.join('cache', 'games.p')
    cache         = Cache(CACHE_PATH)
    cachedgames   = cache.load_from_cache()

    URLS_MAPPING  = os.path.join('mappings', 'urlsmapping.txt')
    urlsmapping   = Mapper(URLS_MAPPING)

    steamgames    = list(steam.get_list_of_games())

    global _exc_infos

    if (options.threads):
        threads   = options.threads
    else:
        threads   = cpu.get_number_of_cores()
    threadpool    = ThreadPoolExecutor(threads)

    for name in iter(games):
        if (len(_exc_infos)):
            break

        threadpool.submit(get_game_info, threadpool, options, games[name],
                          cachedgames, steamgames, name, urlsmapping)

    threadpool.shutdown(wait=True)
    if (len(_exc_infos)):
        for exc_info in _exc_infos:
            traceback.print_exception(*exc_info)
        raise Exception('An exception was raised in some of the threads, see above.')

    if (options.dryrun):
        return

    newcachedgames = cache.merge_old_new_cache(cachedgames, games)
    cache.save_to_cache(newcachedgames)
    urlsmapping.save_mapping()
