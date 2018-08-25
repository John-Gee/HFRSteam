import asyncio
from enum import Enum, auto
import progressbar

import domparser
import utils
import web


class Rating(Enum):
    Platinum   = auto()
    Gold       = auto()
    Silver     = auto()
    Bronze     = auto()
    Garbage    = auto()


class WineApp():
    def __init__(self, link, rating):
        self.link   = link
        self.rating = rating


async def get_forOneRating(url, rating):
    fullURL = url + rating
    apps   = []
    while (fullURL):
        _, _, page = await web.get_web_page(fullURL)
        document = domparser.load_html(page)

        table = domparser.get_element(document, 'table', class_="whq-table whq-table-full")
        if (table is None):
            break

        apps.extend(domparser.get_texts_and_values(table, 'a', 'href')[2:])
        i = domparser.get_element(document, 'i', class_='fa fa-chevron-right')
        fullURL = None
        if (i is not None):
            a = domparser.get_parent(i)
            if (a is not None):
                fullURL = domparser.get_value(a, 'href')

    print(len(apps), 'apps for rating', rating)
    return apps, rating


async def get_ratings():
    URL = 'https://appdb.winehq.org/objectManager.php?sClass=application&sTitle=Browse+Applications&iappVersion-ratingOp0=5&sOrderBy=appName&bAscending=true&iItemsPerPage=200&sappVersion-ratingData0='

    ratings = utils.DictCaseInsensitive()

    tasks   = []
    for e in Rating:
        tasks.append(asyncio.ensure_future(get_forOneRating(URL, e.name)))
    await asyncio.gather(progressbar.progress_bar(tasks))
    for task in tasks:
        apps   = task.result()[0]
        rating = task.result()[1]
        for app in apps:
            if (app[0] in ratings):
                ratings[app[0]].append(WineApp(app[1], rating))
            else:
                ratings[app[0]] = [WineApp(app[1], rating)]
    return ratings


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    web.create_session()
    tasks = [asyncio.ensure_future(get_ratings())]
    loop.run_until_complete(asyncio.gather(*tasks))
    ratings = tasks[0].result()
    print(len(ratings))
    web.close_session()
