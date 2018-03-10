import asyncio
import datetime
import functools
import logging
import tqdm
import traceback

import steam
import styledprint
import threadpool
import web


def get_newgame_info(local_applist, name, appid, typ, tasks, future):
    if (not future.done()):
        styledprint.print_error('the future not done!')
        # Memory cleanup
        tasks.remove(future)
        return
    if (future.cancelled()):
        styledprint.print_error('the future has been canceled!')
        # Memory cleanup
        tasks.remove(future)
        return
    exception = future.exception()
    if (exception):
        styledprint.print_error('the future has an exception: {}'.format(exception))
        # Memory cleanup
        tasks.remove(future)
        return

    page, _, _  = future.result()
    document, _ = steam.get_document(page, name)

    # Memory cleanup
    tasks.remove(future)

    logging.debug('got document for name {} ? {}'.format(name, document != None))
    shortlink   = '{0}/{1}'.format(typ, appid)
    titles      = steam.get_titles(document, shortlink) if (document) else {}
    logging.debug('got titles {0} for name {1}'.format(titles, name))
    if (shortlink not in titles):
        titles[shortlink] = []
    titles[shortlink].append(name)

    for shortlink in titles.keys():
        logging.debug('shortlink {0} for name {1}'.format(shortlink, name))
        t, a = shortlink.split('/')
        for title in titles[shortlink]:
            logging.debug('title {0} for shortlink {1} for name {2}'.format(title, shortlink, name))
            if (title):
                if (title not in local_applist):
                    local_applist[title] = []
                    logging.debug('title {} was not in applist'.format(title))
                if ((a, t) not in local_applist[title]):
                    local_applist[title].append((a, t))
                    logging.debug('tuple {} was not in applist for title {}'.format((a, t), title))
    logging.debug('appid {0} done for name {1}'.format(appid, name))


async def progress_bar(tasks):
    for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        if (f):
            await f


def refresh_applist(loop, dryrun, games, from_scratch=False, max_apps=None):
    styledprint.print_info_begin('AppList Refresh')
    if (from_scratch):
        local_applist = {}
    else:
        local_applist   = steam.get_applist_from_local()
    styledprint.print_info('Apps in cache at start:', len(local_applist))
    foreign_applist = steam.get_applist_from_server(max_apps)
    styledprint.print_info('Apps in server:', len(foreign_applist))

    try:
        calname = 'refresh_applist'
        tasks = []
        for name in foreign_applist:
            for app in foreign_applist[name]:
                if ((name in local_applist) and (app in local_applist[name])):
                    continue
                appid, typ     = app
                link           = steam.get_store_link(appid, typ)
                f = asyncio.ensure_future(steam.get_page(link, name))
                f.add_done_callback(functools.partial(
                    threadpool.submit_job_from,
                    calname,
                    get_newgame_info,
                    local_applist,
                    name,
                    appid,
                    typ,
                    tasks))
                tasks.append(f)
        if (len(tasks)):
            styledprint.print_info('async tasks:')
            loop.run_until_complete(progress_bar(tasks))
            threadpool.wait_calname(calname)
    except Exception as e:
        styledprint.print_error('Error happened while running the async loop:', e)
        styledprint.print_error(traceback.format_exc())
        pass

    styledprint.print_info('Apps in cache at end (duplicate names not in the count):', len(local_applist))
    if (not dryrun):
        logging.debug('not dryrun so saving local_applist to disk')
        steam.save_applist_to_local(local_applist)
    for game in local_applist:
        if(not game.lower().endswith('demo')):
            games[game] = local_applist[game]
    styledprint.print_info('Apps in cleaned cache:', len(games))
    styledprint.print_info_end('AppList Refresh')


if __name__ == '__main__':
    logging.basicConfig(filename='mylog.log',
                        filemode = 'w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    styledprint.set_verbosity(2)
    loop = asyncio.get_event_loop()
    #loop.set_debug(True)
    threadpool.create(16, loop)
    web.create_session(loop)
    try:
        refresh_applist(loop, False, {}, False)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    web.close_session()
    threadpool.shutdown(wait=True)
    # this genereates a stack overflow
    # when the loop was previously stopped
    # loop.close()
