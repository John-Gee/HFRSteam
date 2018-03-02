import steam
import styledprint
import threadpool


def get_newgame_info(local_applist, name, values):
    appid, typ = values
    link           = steam.get_store_link(appid, typ)
    document, _, _ = steam.get_pagedocument(link, name)
    shortlink      = '{0}/{1}'.format(typ, appid)
    titles         = steam.get_titles(document, shortlink) if (document) else {}
    if (shortlink not in titles):
        titles[shortlink] = []
    titles[shortlink].append(name)

    for link in sorted(titles.keys()):
        t, a = link.split('/')
        for title in titles[link]:
            if ((title) and (title not in local_applist)):
                local_applist[title] = (a, t)


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

    styledprint.print_info('Apps in cache at end:', len(local_applist))
    if (not dryrun):
        steam.save_applist_to_local(local_applist)
    for game in local_applist:
        if(not game.lower().endswith('demo')):
            games[game] = local_applist[game]
    styledprint.print_info('Apps in cleaned cache:', len(games))
    styledprint.print_info_end('AppList Refresh')


if __name__ == '__main__':
    threadpool.create(8)
    refresh_applist(False, {}, False)
