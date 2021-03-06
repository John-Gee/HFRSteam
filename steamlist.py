import asyncio
import datetime
import functools
import logging
import tqdm
import traceback
import uvloop

import parallelism
import progressbar
import steam
import styledprint
import utils
import web


def get_newgame_info(name, appid, typ, page):
    local_applist = {}
    document, _   = steam.get_document(page, name)
    logging.debug('got document for name {} ? {}'.format(name, document != None))
    shortlink     = '{0}/{1}'.format(typ, appid)
    titles        = steam.get_titles(document, shortlink) if (document is not None) else {}
    logging.debug('got titles {0} for name {1}'.format(titles, name))
    if (shortlink not in titles):
        titles[shortlink] = []
    titles[shortlink].append(name)

    for shortlink in titles.keys():
        t, a = shortlink.split('/')
        for title in titles[shortlink]:
            if (title):
                if (title not in local_applist):
                    local_applist[title] = []
                if ((a, t) not in local_applist[title]):
                    local_applist[title].append((a, t))
    logging.debug('appid {0} done for name {1}'.format(appid, name))
    return local_applist


def poolsubmit(calname, get_newgame_info, name, appid, typ,
               tasks, future):
    exception = future.exception()
    if (exception):
        styledprint.print_error('the future has an exception: {}'.format(exception))
        styledprint.print_error(traceback.format_exc())
    else:
        page, _, _ = future.result()
        parallelism.submit_job_from(calname, get_newgame_info, name,
                                    appid, typ, page)

    # Memory cleanup
    tasks.remove(future)


def merge_applists(first, second):
    for name in second:
        if (name in first):
            styledprint.print_debug('{} in first'.format(name))
            for t in second[name]:
                if (t not in first[name]):
                    styledprint.print_debug('t {} not in first[name]'.format(t))
                    first[name].append(t)
                else:
                    styledprint.print_debug('t {} in first[name]'.format(t))
        else:
            styledprint.print_debug('{} not in first'.format(name))
            first[name] = second[name]


async def refresh_applist(dryrun, skip, from_scratch=False, max_apps=None):
    local_applist = await steam.get_applist_from_local()
    if(skip):
        return local_applist

    async with web.Session(limit_per_host=20) as webSession:
        foreign_applist = await steam.get_applist_from_server(webSession, max_apps)
        styledprint.print_info('Apps in server:', len(foreign_applist))
        styledprint.print_info('Apps in cache at start:', len(local_applist))
        calname = 'refresh_applist'
        try:
            tasks = []
            for name in foreign_applist:
                for app in foreign_applist[name]:
                    if ((not from_scratch) and
                        (name in local_applist) and
                        (app in local_applist[name])):
                        continue
                    appid, typ = app
                    link       = steam.get_store_link(appid, typ)
                    f          = asyncio.ensure_future(steam.get_page(link, name,
                                                                      webSession))
                    f.add_done_callback(functools.partial(poolsubmit, calname,
                                                        get_newgame_info, name,
                                                        appid, typ, tasks))
                    tasks.append(f)

            if (len(tasks)):
                styledprint.print_info('async tasks:')
                await asyncio.gather(progressbar.progress_bar(tasks))
        except Exception as e:
            styledprint.print_error('Error happened while running the async loop:', e)
            styledprint.print_error(traceback.format_exc())
            pass
        fs = parallelism.wait_calname(calname)
        for f in fs:
            ext_applist = f.result()
            merge_applists(local_applist, ext_applist)
        styledprint.print_info('Apps in cache at end (duplicate names not in the count):', len(local_applist))

        if (not dryrun):
            logging.debug('not dryrun so saving local_applist to disk')
            await steam.save_applist_to_local(local_applist)

    games = utils.DictCaseInsensitive()
    for game in local_applist:
        if(not game.lower().endswith('demo')):
            games[game] = local_applist[game]
    styledprint.print_info('Apps in cleaned cache:', len(games))
    return games


if __name__ == '__main__':
    logging.basicConfig(filename='mylog.log',
                        filemode = 'w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    styledprint.set_verbosity(1)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    #loop.set_debug(True)
    parallelism.create_pool(8, loop)

    applist = {'Endless Legend': [(289130, 'app')]}

    try:
        tasks = [asyncio.ensure_future(refresh_applist(dryrun=True,
                                                       skip=False,
                                                       from_scratch=False,
                                                       max_apps=None))]
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    parallelism.shutdown_pool(wait=True)
    # this genereates a stack overflow
    # when the loop was previously stopped
    # loop.close()
