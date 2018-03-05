import faulthandler
import logging
import signal

import steam
import styledprint
import threadpool


def get_newgame_info(local_applist, name, apps):
    logging.debug('len(apps): {0} for name: {1}'.format(len(apps), name))
    for app in apps:
        appid, typ     = app
        link           = steam.get_store_link(appid, typ)
        logging.debug('got link {0} for name {1}'.format(link, name))
        document, _, _ = steam.get_pagedocument(link, name)
        logging.debug('got document for name {0} ?'.format(name, document != None))
        shortlink      = '{0}/{1}'.format(typ, appid)
        titles         = steam.get_titles(document, shortlink) if (document) else {}
        logging.debug('got titles {0} for name {1}'.format(titles, name))
        if (shortlink not in titles):
            titles[shortlink] = []
        titles[shortlink].append(name)

        for shortlink in sorted(titles.keys()):
            logging.debug('shortlink {0} for name {1}'.format(shortlink, name))
            t, a = shortlink.split('/')
            for title in titles[shortlink]:
                logging.debug('title {0} for shortlink {1} for name {2}'.format(title, shortlink, name))
                if (title):
                    if (title not in local_applist):
                        local_applist[title] = []
                    if ((a, t) not in local_applist[title]):
                        local_applist[title].append((a, t))
    logging.debug('Got all the info for name: ' + name)

def refresh_applist(dryrun, games, from_scratch=False):
    styledprint.print_info_begin('AppList Refresh')
    if (from_scratch):
        local_applist = {}
    else:
        local_applist   = steam.get_applist_from_local()
    styledprint.print_info('Apps in cache at start:', len(local_applist))
    foreign_applist = steam.get_applist_from_server()
    styledprint.print_info('Apps in server:', len(foreign_applist))

    threadpool.submit_jobs(((get_newgame_info, local_applist, name, foreign_applist[name])
                            for name in iter(foreign_applist)
                            if name not in local_applist))

    logging.debug('threadpool.submit_jobs done')
    styledprint.print_info('Apps in cache at end (duplicate names not in the count):', len(local_applist))
    if (not dryrun):
        steam.save_applist_to_local(local_applist)
    for game in local_applist:
        if(not game.lower().endswith('demo')):
            games[game] = local_applist[game]
    styledprint.print_info('Apps in cleaned cache:', len(games))
    styledprint.print_info_end('AppList Refresh')


if __name__ == '__main__':
    logging.basicConfig(filename='mylog.log', filemode = 'w', level=logging.DEBUG)
    threadpool.create(16)
    styledprint.set_verbosity(1)
    refresh_applist(False, {}, True)
