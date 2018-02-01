import calendar
import datetime
from dateutil import parser
import os
import re

from game import Category, Game
import domparser
import namematching
import web


APPLIST_URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
_games = dict()
_applist = web.get_json_data_from_url(APPLIST_URL)
for app in iter(_applist['applist']['apps']):
    name = app['name'].lower()
    if (name not in _games):
        _games[name] = app['appid']


def get_appid(name):
    cleanname = name.lower()
    if (cleanname in _games):
        return _games[cleanname]
    else:
        return ''


def get_list_of_games():
    return _games.keys()


def get_urlmapping_fromappid(appid):
    # defaulting to the standard game url for now
    return 'app/{0}'.format(appid)


def get_store_info_from_appid(game, name, appid):
    game.store.link = 'http://store.steampowered.com/{0}'.format(
                       get_urlmapping_fromappid(appid))
    get_store_info(game, name)


def get_store_info_from_url(game, name, url):
    game.store.link= 'http://store.steampowered.com/' + url
    get_store_info(game, name)


def get_store_info(game, name):
    url, status, page = web.get_utf8_web_page(game.store.link)

    if (game.store.link not in url):
        game.store.description = 'The app is not on steam anymore.'
        print('The page for app {0} redirects somewhere else'
              .format(name))
        return

    document = domparser.load_html(page)

    sorry_block = domparser.get_element(document, 'h2',
                                        class_='pageheader',
                                        string='Oops, sorry!')

    if (sorry_block):
        game.store.description = domparser.get_text(document, 'span',
                                              class_="error")
        print('The page for game {0} shows an error: {1}'
              .format(name, game.store.description))
        return

    if ( ('/sub/' in game.store.link) or ('/bundle/' in game.store.link)):
        get_collection_info(game, name, document)
    elif ('/app/' in game.store.link):
        get_standalone_info(game, name, document)
    else:
        print('Unknown type of link {0}'.format(game.store.link))

    # middle right column
    game.store.genres       = get_game_genres(document)
    game.store.details      = get_game_details(document)

    price_date              = str(datetime.datetime.now().date())
    game.store.price_date   = ('{0} {1}, {2}'
                         .format(calendar.month_abbr[int(price_date[5:7])],
                                 price_date[8:], price_date[:4]))


def get_standalone_info(game, name, document):
    # middle left column
    game_left_column    = domparser.get_element(document, 'div',
                                                class_='leftcol game_description_column')

    purchase_block      = domparser.get_element(game_left_column, 'div',
                                                id='game_area_purchase')
    game.store.category = get_game_category(purchase_block)
    game.store.price    = get_game_price(purchase_block, name)
    game.store.os       = get_game_os(game_left_column)

    # top right header
    glance_ctn_block        = domparser.get_element(document, 'div',
                                                    class_='glance_ctn')
    game.store.image        = get_game_image(glance_ctn_block)
    game.store.avg_review,\
    game.store.cnt_review   = get_game_review(glance_ctn_block, name)
    game.store.release_date = get_game_release_date(glance_ctn_block)
    game.store.tags         = get_game_tags(glance_ctn_block)

    if (game.store.category is Category.Game):
        game.store.description  = get_game_description(glance_ctn_block)
    elif (game.store.category is Category.DLC):
        game.store.description  = get_dlc_description(document)
    else:
        game.store.description  = ''
        print('The category {0} is not implemented yet!'.format(game.store.category.name))


def get_collection_info(game, name, document):
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
        get_store_info(itemgame, itemname)
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
        print('Cannot find the review block for game: {0}'.format(name))
        return '', '0'

    user_reviews_block = domparser.get_parent(overall_block, 'div')

    reviewCount = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='reviewCount')

    ratingValue = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='ratingValue')

    if (reviewCount):
        return int(ratingValue), int(reviewCount)
    return None, None


def get_game_release_date(glance_ctn_block):
    date = domparser.get_text(glance_ctn_block, 'div',
                              class_='date')
    if (date):
        return parser.parse(date.strip(), fuzzy_with_tokens=True)

    return None


def get_game_category(purchase_block):
    dlc_block = domparser.get_element(purchase_block, 'div',
                                      class_='game_area_dlc_bubble game_area_bubble')
    if (dlc_block is None):
        return Category.Game
    else:
        return Category.DLC


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
            matches = namematching.get_match(name.lower(), names, len(names))
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
                print('Unexpected price: {0} for {1}'.format(price, name))
                return -1

    play_game_span = domparser.get_element(purchase_block, 'span',
                                           string='Play Game')
    if (play_game_span):
        return 0

    download_span  = domparser.get_element(purchase_block, 'span',
                                           string='Download')
    if (download_span):
        return 0

    print('No price found for {0}'.format(name))
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


# simple test
if __name__ == '__main__':
    game = Game()
    get_store_info_from_appid(game, 'STAR WARS™: TIE Fighter Special Edition', '355250')
    print(game.store.price)
