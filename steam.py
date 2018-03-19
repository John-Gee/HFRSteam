import aiofiles
import asyncio
import calendar
import datetime
from dateutil import parser
import json
import logging
import os
import re

from game import Category, Game
import domparser
import namematching
import styledprint
import utils
import web


def get_games_from_applist(applist, max_apps=None):
    games = {}
    i = 0
    for app in iter(json.loads(applist)['applist']['apps']):
        if ((max_apps is not None) and (i >= max_apps)):
            break
        if (app['name'] not in games):
            games[app['name']] = []
        if ('type' in app):
            games[app['name']].append((app['appid'], app['type']))
        else:
            games[app['name']].append((app['appid'], 'app'))
        i += 1
    return games


async def save_applist_to_local(applist):
    if ((not applist) or (not len(applist))):
        logging.debug('no applist to save to local')
        return

    APPLIST_LOCAL = 'steamlist/AppList.json'
    js_dict       = {}
    data          = []

    for name in iter(applist):
        for app in applist[name]:
            if('app' == app[1]):
                data.append({'appid': int(app[0]), 'name': name})
            else:
                data.append({'appid': int(app[0]), 'name': name,
                            'type': app[1]})
    sorted_data = sorted(data, key=lambda k: k['appid'])
    js_dict['applist'] = {'apps': sorted_data}
    if (not os.path.exists('steamlist')):
        os.makedirs('steamlist')
    async with aiofiles.open(APPLIST_LOCAL, 'w', encoding='utf8') as f:
        content = json.dumps(js_dict, sort_keys=True, indent='\t', ensure_ascii=False)
        await f.write(content)


async def get_applist_from_local():
    APPLIST_LOCAL = 'steamlist/AppList.json'
    if (os.path.exists(APPLIST_LOCAL)):
        async with aiofiles.open(APPLIST_LOCAL, 'r', encoding='utf8') as f:
            applist = await f.read()
            return get_games_from_applist(applist)
    return {}


async def get_applist_from_server(max_apps=None):
    APPLIST_URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
    applist     = (await web.get_web_page(APPLIST_URL))[2]
    return get_games_from_applist(applist, max_apps)


def get_store_link(appid, typ):
    return 'http://store.steampowered.com/{0}/{1}'.format(typ, appid)


async def get_store_info_from_appid(game, name, appid, typ):
    game.store.link = get_store_link(appid, typ)
    return await get_store_info(game, name)


async def get_store_info_from_url(game, name, url):
    game.store.link= 'http://store.steampowered.com/' + url
    return await get_store_info(game, name)


async def get_page(storelink, name):
    badurl = 'http://store.steampowered.com/'
    url, status, page = await web.get_web_page(storelink, badurl)
    if ((not url) or ('http://store.steampowered.com/' == url)):
        description = 'The app is not on steam anymore.'
        logging.debug('The page for app {0} redirects somewhere else'
                      .format(name))
        return None, description, url

    return page, None, url

def get_document(page, name):
    document = domparser.load_html(page)

    if ('Oops, sorry!' in document):
        description = domparser.get_text(document, 'span',
                                         class_="error")
        logging.debug('The page for game {0} shows an error: {1}'
                       .format(name, description))
        return None, description

    return document, None


async def get_store_info(game, name):
    page, description, url     = await get_page(game.store.link, name)
    if (not page):
        game.store.description = description
        return False

    document, description = get_document(page, name)

    if (not document):
        game.store.description = description
        return False
    game.store.link = re.sub(r'(http://store.steampowered.com/[^/]*/[^/]*)/.*',
                              r'\1', url, flags=re.IGNORECASE)

    if ( ('/sub/' in game.store.link) or ('/bundle/' in game.store.link)):
        await get_collection_info(game, name, document)
    elif ('/app/' in game.store.link):
        get_standalone_info(game, name, document)
    else:
        styledprint.print_info('Unknown type of link {0}'
                               .format(game.store.link))

    # middle right column
    game.store.genres     = get_game_genres(document)
    game.store.details    = get_game_details(document)

    price_date            = str(datetime.datetime.now().date())
    game.store.price_date = ('{0} {1}, {2}'
                             .format(calendar.month_abbr[int(price_date[5:7])],
                                     price_date[8:], price_date[:4]))
    return True


def get_standalone_info(game, name, document):
    # middle left column
    game_left_column    = domparser.get_element(document, 'div',
                                                class_='leftcol game_description_column')

    purchase_block      = domparser.get_element(game_left_column, 'div',
                                                id='game_area_purchase')
    game.store.category = get_game_category(purchase_block, document)
    game.store.price    = get_game_price(purchase_block, name)
    game.store.os       = get_game_os(game_left_column)

    # top right header
    glance_ctn_block        = domparser.get_element(document, 'div',
                                                    class_='glance_ctn')
    game.store.image        = get_game_image(glance_ctn_block)
    game.store.avg_review,\
    game.store.cnt_review   = get_game_review(glance_ctn_block, name)
    game.store.release_date = get_game_release_date(glance_ctn_block, name)
    game.store.tags         = get_game_tags(glance_ctn_block)

    if (game.store.category in [Category.Game, Category.Video]):
        game.store.description  = get_game_description(glance_ctn_block)
    elif (game.store.category is Category.DLC):
        game.store.description  = get_dlc_description(document)
    else:
        game.store.description  = ''
        styledprint.print_info('The category {0} is not implemented yet!'
                               .format(game.store.category.name))

    game.store.languages    = get_game_languages(document)


async def get_collection_info(game, name, document):
    game.store.category = Category.Collection

    descriptions        = list()
    OS                  = list()
    release_dates       = list()
    avg_reviews         = 0
    cnt_reviews         = 0
    tags                = list()
    game_left_column    = domparser.get_element(document, 'div',
                                                class_='leftcol game_description_column')
    items               = domparser.get_elements(game_left_column, 'div',
                                                 class_='tab_item ')
    if (len(items) == 0):
        items           = domparser.get_elements(game_left_column, 'div',
                                                 class_='tab_item')

    for item in items:
        itemlink        = domparser.get_value(item, 'a', 'href',
                                              class_='tab_item_overlay')
        itemname        = domparser.get_text(item, 'div',
                                             class_='tab_item_name')
        descriptions.append('- {0}'.format(itemname))

        itemgame            = Game()
        itemgame.store.link = itemlink
        await get_store_info(itemgame, itemname)
        for o in itemgame.store.os:
            if (o not in OS):
                OS.append(o)
        if (itemgame.store.release_date):
            release_dates.append(itemgame.store.release_date)
        # to average the reviews
        if (itemgame.store.cnt_review):
            avg_reviews += itemgame.store.cnt_review * itemgame.store.avg_review
            cnt_reviews += itemgame.store.cnt_review
        for tag in itemgame.store.tags:
            if (tag not in tags):
                tags.append(tag)

    game.store.image            = get_collection_image(game_left_column)
    game.store.description      = 'Items included in this package:{0}{1}'.format(
        os.linesep, os.linesep.join(descriptions))
    game.store.os               = sorted(OS)
    if (len(release_dates)):
        game.store.release_date = sorted(release_dates)[-1]
    if (cnt_reviews):
        game.store.avg_review   = int(avg_reviews / cnt_reviews)
        game.store.cnt_review   = int(cnt_reviews/len(items))
    game.store.tags             = sorted(tags)

    purchase_block      = domparser.get_element(game_left_column, 'div',
                                                id='game_area_purchase')
    game.store.price    = get_game_price(purchase_block, name)


def get_game_image(glance_ctn_block):
    return domparser.get_value(glance_ctn_block, 'img', 'src',
                               class_='game_header_image_full')


def get_collection_image(game_left_column):
    return domparser.get_value(game_left_column, 'img', 'src',
                               class_='package_header')


def get_game_description(glance_ctn_block):
    description =  domparser.get_text(glance_ctn_block, 'div',
                                      class_='game_description_snippet')

    if (description):
        return description.replace('"', '').strip()

    return None


def get_dlc_description(document):
    widget_create_block = domparser.get_element(document, 'div',
                                                id='widget_create')

    if (widget_create_block):
        description = domparser.get_value(widget_create_block, 'textarea',
                                      'placeholder')
        if (description):
            return description.replace('"', '').strip()

    return None


def get_game_review(glance_ctn_block, name):
    overall_block = domparser.get_element(
        glance_ctn_block, 'div', class_='subtitle column all',
        string='All Reviews:')

    if (overall_block == None):
        styledprint.print_info('Cannot find the review block for game: {0}'
                               .format(name))
        return '', '0'

    user_reviews_block = domparser.get_parent(overall_block, 'div')

    reviewCount = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='reviewCount')

    ratingValue = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='ratingValue')

    if (reviewCount):
        return int(ratingValue), int(reviewCount)
    return None, None


def get_game_release_date(glance_ctn_block, name):
    date = domparser.get_text(glance_ctn_block, 'div',
                              class_='date')
    if (date):
        try:
            return parser.parse(date.strip(), fuzzy_with_tokens=True)
        except:
            styledprint.print_info('date: {0} for game: {1} is no good'.format(date, name))
            pass

    return None


def get_game_category(purchase_block, document):
    dlc_block = domparser.get_element(purchase_block, 'div',
                                      class_='game_area_dlc_bubble game_area_bubble')
    if (dlc_block):
        return Category.DLC

    videos_href = domparser.get_element(document, 'a',
                                      text='All Streaming Videos')
    if (videos_href):
        return Category.Video

    return Category.Game


def get_game_price(purchase_block, name):
    wrappers = domparser.get_elements(purchase_block, 'div',
                                      class_='game_area_purchase_game_wrapper')

    if (wrappers):
        names  = list()
        prices = list()
        for wrapper in wrappers:
            names.append(domparser.get_text(wrapper, 'h1')[4:].lower())
            price = domparser.get_text(wrapper, 'div',
                                       class_='game_purchase_price price')
            if(not price):
                price = domparser.get_text(wrapper, 'div',
                                           class_='discount_final_price')
            prices.append(price)

        sortedprices = list()
        if (len(names)):
            matches = namematching.get_matches(name.lower(), names, len(names))
            for match in matches:
                index = names.index(match)
                sortedprices.append(prices[index])
        if (not len(sortedprices)):
            sortedprices = prices
    else:
        sortedprices = domparser.get_texts(purchase_block, 'div',
                                           class_='game_purchase_price price')
        if(not sortedprices):
                sortedprices = domparser.get_texts(purchase_block, 'div',
                                                   class_='discount_final_price')

    for price in sortedprices:
        if (price):
            # we got the wrong div
            if ('demo' in price.lower()):
                continue

            price = price.replace('$', '').replace('€', '').strip()
            if (price.replace('.','',1).isdigit()):
                return float(price)
            elif (('free' in price.lower()) or ('play' in price.lower())):
                return 0
            else:
                styledprint.print_info('Unexpected price: {0} for {1}'
                                       .format(price, name))
                return -1

    play_game_span = domparser.get_element(purchase_block, 'span',
                                           string='Play Game')
    if (play_game_span):
        return 0

    download_span  = domparser.get_element(purchase_block, 'span',
                                           string='Download')
    if (download_span):
        return 0

    styledprint.print_info('No price found for {0}'.format(name))
    return -1


def get_game_os(game_left_column):
    os = domparser.get_values(game_left_column, 'div', 'data-os',
                              class_=re.compile('game_area_sys_req sysreq_content'))
    os = [o.replace('linux', 'Linux')
           .replace('mac', 'Mac OS X')
           .replace('win', 'Windows')
          for o in os]

    os.sort()
    return os


def get_game_genres(document):
    genre_title = domparser.get_element(document, 'b', string='Genre:')
    if (genre_title):
        return domparser.get_next_siblings_text(genre_title, 'a')
    return list()


def get_game_details(document):
    details_block = domparser.get_element(document, 'div',
                                    class_='rightcol game_meta_data')
    if (details_block):
        return domparser.get_texts(details_block, 'div',
                                   class_='game_area_details_specs')
    return list()


def get_game_tags(glance_ctn_block):
    tags_block = domparser.get_element(glance_ctn_block, 'div',
                                       class_='glance_tags popular_tags')
    if (tags_block):
        # tags are by default in the format:
        # \r\n\t\t\t\t\t\t\t\t\t\t\t\tTAG\t\t\t\t\t\t\t\t\t\t\t\t
        return sorted(list(map(lambda s: s.strip(),
                               domparser.get_texts(tags_block, 'a'))))
    return list()


def get_game_languages(document):
    language_block = domparser.get_element(document, 'table',
                                    class_='game_language_options')
    if (language_block):
        return domparser.get_texts(language_block, 'td',
                                   class_='ellipsis')
    return list()


def get_titles(document, shortlink):
    titles = {}
    titles[shortlink] = [domparser.get_text(document, 'div', class_='apphub_AppName')]

    wrappers = domparser.get_elements(document, 'div',
                                      class_=re.compile('game_area_purchase_game_wrapper'))

    if (wrappers):
        for wrapper in wrappers:
            if (any (i in ['Bundle info', 'Package info']
                     for i in domparser.get_texts(wrapper, 'span'))):
                href = domparser.get_value(wrapper, 'a', 'href',
                                        class_=re.compile('btnv6_blue_blue_innerfade'))
                link = re.sub(r'.*steampowered.com/([^/]+/[^/]+)/.*',
                              r'\1', href, flags=re.IGNORECASE)
            else:
                link = shortlink
            title = domparser.get_text(wrapper, 'h1')[4:]
            if (title):
                if (title.lower().endswith('demo')):
                    continue
                #merge the regexp?
                title = re.sub(r'\s*Buy ?', r'', title)
                title = re.sub(r'(\n|\r|\t).*', r'', title)
                if (link not in titles):
                    titles[link] = []
                if (title not in titles[link]):
                    titles[link].append(title)
    return titles


# simple test
if __name__ == '__main__':
    logging.basicConfig(filename='mylog.log', filemode = 'w', level=logging.DEBUG)
    game = Game()
    styledprint.set_verbosity(2)
    typ = 'app'
    appid = '100'
    name = 'Counter-Strike: Condition Zero'
    storelink   = get_store_link(appid, typ)
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    web.create_session(loop)
    try:
        page, _, _  = loop.run_until_complete(get_page(storelink, name))
        document, _ = get_document(page, name)
        titles      = get_titles(document, '{}/{}'.format(typ, appid))
        print(titles)
    finally:
        web.close_session()
        loop.close()
