import asyncio
from enum import Enum, auto


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

        table = domparser.get_element(document, 'table')
        if not table:
            break

        domparser.remove_element(table, 'thead')
        apps.extend(domparser.get_texts_and_values(table, 'a', 'href'))

        i = domparser.get_element(document, 'i', class_='fa fa-chevron-right')
        fullURL = None
        if (i):
            a = domparser.get_parent(i, 'a')
            if (a):
                fullURL = domparser.get_value(a, 'href')

    print(len(apps), 'apps for rating', rating)
    return apps

async def get_ratings():
    URL = 'https://appdb.winehq.org/objectManager.php?sClass=application&sTitle=Browse+Applications&iappVersion-ratingOp0=5&sOrderBy=appName&bAscending=true&iItemsPerPage=200&sappVersion-ratingData0='

    ratings = utils.DictCaseInsensitive()
    for e in Rating:
        for k in await get_forOneRating(URL, e.name):
            if (k[0] in ratings):
                ratings[k[0]].append(WineApp(k[1], e.name))
            else:
                ratings[k[0]] = [WineApp(k[1], e.name)]
    return ratings


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    web.create_session(1)
    tasks = [asyncio.ensure_future(get_ratings())]
    loop.run_until_complete(asyncio.gather(*tasks))
    ratings = tasks[0].result()
    print(len(ratings))
    web.close_session()
