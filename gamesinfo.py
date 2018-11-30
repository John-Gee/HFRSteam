import asyncio
import copy
from datetime import datetime
import os
import sys
import traceback
import uvloop

from cache import Cache
from game import Category
from game import StoreData
from mapper import Mapper
import namematching
import parallelism
import progressbar
import steam
import styledprint
import utils
import web


def get_appid_and_type(name, games, appidstried):
    if (name in games):
        for app in games[name]:
            if (app[0] not in appidstried):
                return app
    return None, None


def get_clean_matches(name, dic):
    return namematching.get_clean_matches(name, dic.keys(), 0.92)


def get_appid_and_type_from_namematching(origname, name, games, appidstried,
                                         matches):
    while (True):
        if (matches is None):
            matches = get_clean_matches(name, games)

        if (len(matches) == 0):
            return None, None

        matchedname = matches[0]
        if (matchedname):
            score         = namematching.get_match_score(name, matchedname)
            styledprint.print_info('Matched {0} with {1} at score {2}'
                                   .format(origname, matchedname, score))
            appid, typ    = get_appid_and_type(matchedname, games, appidstried)
            if (appid):
                return appid, typ
            else:
                matches.pop(0)
        else:
            return None, None


async def get_game_info(options, game, cachedgames, steamgames, winedb,
                  cleansteamgames, cleanwinedb, name, urlsmapping, webSession):
    try:
        if ((not options.all) and (not game.hfr.is_available)):
            # Ignoring not available games for now
            # it may be better in the future to ignore them in output
            # or allow the user to do so in the html page.
            return

        if (name in cachedgames):
            # Whether the cache is ignored or not,
            # if a game cached has a gift_date we keep it
            if (cachedgames[name].hfr.gift_date):
                game.hfr.gift_date = cachedgames[name].hfr.gift_date

            if (not options.ignorecache):
                game.store         = cachedgames[name].store
                game.wine          = cachedgames[name].wine

        # query the store if:
        # - not cacheonly
        # - not in cache
        # - in cache and to be refreshed
        if ((not options.cacheonly) and
            ((game.store.link is None) or ((options.game) and
                                           (options.game.lower()
                                            in name.lower())))):

            # keep the old information if there is no new one
            if (game.store.link):
                storeBU = copy.deepcopy(game.store)
                worked  = await steam.get_store_info(game, name, webSession)
                if (worked):
                    styledprint.print_info('Info for game {0} was retrieved, {1}'
                                           .format(name,
                                                   str(datetime.now().time())))
                else:
                    game.store = storeBU
            else:
                mapping = urlsmapping.get_mapping(name)

                if (mapping == None):
                    appidstried = []
                    matches     = None
                    while (True):
                        appid, typ = get_appid_and_type(name, steamgames, appidstried)
                        if (appid):
                            styledprint.print_debug('The game {0} got its appid simply'
                                                    .format(name))
                        elif (options.fuzzymatching):
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
                                                                                matches)

                        if ((appid in appidstried) or (not appid)):
                            game.store = StoreData()
                            game.store.description = 'The game was not found in the steam db'
                            styledprint.print_error('{0}: {1}'
                                                    .format(game.store.description, name))
                            return
                        else:
                            appidstried.append(appid)

                            if (await steam.get_store_info_from_appid(game,
                                                                            name,
                                                                            appid,
                                                                            typ,
                                                                            webSession)):
                                break

                else:
                    url      = mapping[0]

                    if (url == 'ignore'):
                        styledprint.print_debug('{0} cannot be found and is to be ignored'
                                                .format(name))
                        return

                    styledprint.print_debug('URL mapping found for game {0}'
                                            .format(name))
                    await steam.get_store_info_from_url(game, name,
                                                        url, webSession)
                    # overwriting the steam provided category
                    if (len(mapping) == 2):
                        game.store.category = Category[mapping[1].upper()]
                        game.store.override = True

                styledprint.print_info('Info for game {0} was retrieved, {1}'
                                    .format(name,
                                            str(datetime.now().time())))

        if (name in winedb):
            game.wine = winedb[name]
        elif (options.fuzzymatching):
            cleanname = namematching.nameclean(name)
            if (cleanname in cleanwinedb):
                game.wine = cleanwinedb[cleanname]
            else:
                cleanmatches = get_clean_matches(cleanname, cleanwinedb)
                if (len(cleanmatches)):
                    game.wine = cleanwinedb[cleanmatches[0]]

    except Exception as e:
        styledprint.print_error('An exception was raised for', name)
        raise e


# TODO
# need to cache nameclean
# last try was way slower than without cache
def clean_names(names):
    cleannames = utils.DictCaseInsensitive()

    for name in names:
        cleanname = namematching.nameclean(name)
        if (cleanname in cleannames):
            for t in names[name]:
                if (t not in cleannames[cleanname]):
                    cleannames[cleanname].append(t)
        else:
            cleannames[cleanname] = names[name]

    return cleannames


def start_loop(subGames, options, cachedgames, steamgames, winedb,
               cleansteamgames, cleanwinedb, urlsmapping, cpuCount):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    webSession = web.Session(limit_per_host=((20/cpuCount) + 1))
    tasks = []
    for name in subGames:
        game = subGames[name]
        tasks.append(asyncio.ensure_future(get_game_info(options, game,
                                                        cachedgames, steamgames,
                                                        winedb, cleansteamgames,
                                                        cleanwinedb, name,
                                                        urlsmapping,
                                                        webSession),
                                           loop=loop))
    loop.run_until_complete(asyncio.gather(progressbar.progress_bar(tasks),
                                                                    loop=loop))
    loop.run_until_complete(webSession.close())
    return subGames


def get_games_info(options, games, steamgames, winedb):
    styledprint.print_info_begin('Pulling Games Information')
    CACHE_PATH      = os.path.join('cache', 'games.p')
    cache           = Cache(CACHE_PATH)
    cachedgames     = cache.load_from_cache()
    cleansteamgames = utils.DictCaseInsensitive()
    cleanwinedb     = utils.DictCaseInsensitive()
    if (options.fuzzymatching):
        parallelism.split_submit_job(steamgames, cleansteamgames, clean_names)
        parallelism.split_submit_job(winedb, cleanwinedb, clean_names)

    URLS_MAPPING    = os.path.join('mappings', 'urlsmapping.txt')
    urlsmapping     = Mapper(URLS_MAPPING)

    parallelism.split_submit_job(games, games, start_loop, options, cachedgames,
                                 steamgames, winedb, cleansteamgames,
                                 cleanwinedb, urlsmapping, parallelism.get_number_of_cores())

    if (not options.dryrun):
        newcachedgames = cache.merge_old_new_cache(cachedgames, games)
        cache.save_to_cache(newcachedgames)
        urlsmapping.save_mapping()

    styledprint.print_info_end('Pulling Games Information Done')


if __name__ == '__main__':
    origname = "My Test1 is the good"
    name     = "MYTEST1ISGOOD"
    games    = {'MYTEST1ISGOOD': [('1', 'app'), ('2', 'app')],
                'MYTEST1ISGOODS': [('3', 'app'), ('4', 'app'), ('5', 'app')],
                'MYTEST1ISSOOOOOGOODSS': [('6', 'app'), ('7', 'app')]}
    appidstried = []
    matches     = []
    appid       = ''
    while (appid != '4'):
        appid, typ = get_appid_and_type_from_namematching(origname, name, games, appidstried,
                                         matches)
        appidstried.append(appid)
        print(appid)
    print('Got the appid needed!')
