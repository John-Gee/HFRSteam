import asyncio
import datetime
import os
import sys
import traceback

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
                  cleansteamgames, cleanwinedb, name, urlsmapping):
    try:
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
                matches     = None
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
                                                                            matches)

                    if ((appid in appidstried) or (not appid)):
                        game.store = StoreData()
                        game.store.description = 'The game was not found in the steam db'
                        styledprint.print_error('{0}: {1}'
                                                .format(game.store.description, name))
                        return
                    else:
                        appidstried.append(appid)

                        if (await steam.instance.get_store_info_from_appid(game,
                                                                           name,
                                                                           appid,
                                                                           typ)):
                            break

            else:
                url      = mapping[0]

                if (url == 'ignore'):
                    styledprint.print_debug('{0} cannot be found and is to be ignored'
                                            .format(name))
                    return

                styledprint.print_debug('URL mapping found for game {0}'
                                        .format(name))
                await steam.instance.get_store_info_from_url(game, name, url)
                # overwriting the steam provided category
                if (len(mapping) == 2):
                    game.store.category = Category[mapping[1].upper()]
                    game.store.override = True

            styledprint.print_info('Info for game {0} was retrieved, {1}'
                                .format(name,
                                        str(datetime.datetime.now().time())))

        if (name in winedb):
            game.wine = winedb[name]
        else:
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


def get_games_info(loop, options, games, steamgames, winedb):
    styledprint.print_info_begin('Pulling games information')
    CACHE_PATH      = os.path.join('cache', 'games.p')
    cache           = Cache(CACHE_PATH)
    cachedgames     = cache.load_from_cache()
    cleansteamgames = clean_names(steamgames)
    cleanwinedb     = clean_names(winedb)

    URLS_MAPPING    = os.path.join('mappings', 'urlsmapping.txt')
    urlsmapping     = Mapper(URLS_MAPPING)

    steam.create()

    tasks = []
    for name in games:
        tasks.append(asyncio.ensure_future(get_game_info(options, games[name],
                                                         cachedgames, steamgames,
                                                         winedb, cleansteamgames,
                                                         cleanwinedb, name,
                                                         urlsmapping)))

    loop.run_until_complete(asyncio.gather(progressbar.progress_bar(tasks)))

    if (not options.dryrun):
        newcachedgames = cache.merge_old_new_cache(cachedgames, games)
        cache.save_to_cache(newcachedgames)
        urlsmapping.save_mapping()

    loop.run_until_complete(steam.close())
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
