import asyncio
from enum import Enum, auto
import progressbar
import uvloop

import domparser
import styledprint
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


def get_apps_from_doc(document):
    table = domparser.get_element(document, 'table', class_="whq-table whq-table-full")
    if (table is None):
        return None

    return domparser.get_texts_and_values(table, 'a', 'href')[2:]


async def get_forOneRating(url, rating):
    fullURL = url + rating
    apps    = []

    _, _, page = await web.get_web_page(fullURL)
    if ((page is None) or
        ('<p class="text-center">No matches found</p>' in page)):
        return apps

    document = domparser.load_html(page)

    pageElem = domparser.get_element(document, 'div', class_='text-center')
    numOfPages = domparser.get_next_siblings_text(pageElem, 'b')[1]

    tasks   = []
    for p in range(2, int(numOfPages) + 1):
        nextURL = '{0}&iPage={1}'.format(fullURL, p)
        tasks.append(web.get_web_page(nextURL))

    #1st page
    apps.extend(get_apps_from_doc(document))
    #others
    for f in asyncio.as_completed(tasks):
        _, _, page = await f
        document   = domparser.load_html(page)
        apps2      = get_apps_from_doc(document)
        if (apps2 is not None):
            apps.extend(apps2)

    print(len(apps), 'apps for rating', rating)
    return apps, rating


async def get_ratings():
    styledprint.print_info_begin('Getting Wine Ratings')
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

    styledprint.print_info_begin('Done Getting Wine Ratings')
    return ratings


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    web.create_session()
    tasks = [asyncio.ensure_future(get_ratings())]
    loop.run_until_complete(asyncio.gather(*tasks))
    ratings = tasks[0].result()
    print(len(ratings))
    web.close_session()
