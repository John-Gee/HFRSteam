import steam
import threadpool


def get_newgame_info(local_applist, name, appid):
    link        = steam.get_store_link_from_appid(appid)
    document, _ = steam.get_pagedocument(link, name)
    titles      = steam.get_titles(document) if (document) else []
    titles.append(name)

    for title in titles:
        if (title not in local_applist):
            local_applist[title] = appid


def refresh_applist(games):
    print('******* AppList Refresh *******')
    local_applist   = steam.get_applist_from_local()
    print('Apps in cache at start:', len(local_applist))
    foreign_applist = steam.get_applist_from_server()
    print('Apps in server:', len(foreign_applist))

    for name in iter(foreign_applist):
        if (name in local_applist):
            continue

        appid = foreign_applist[name]
        threadpool.submit_work(get_newgame_info, local_applist, name, appid)
    threadpool.wait()

    print('Apps in cache now:', len(local_applist))
    steam.save_applist_to_local(local_applist)
    games.update(local_applist)
    print('******* AppList Refresh *******')


if __name__ == '__main__':
    rebuild_applist()
