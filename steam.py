import calendar
import datetime
import os
import re
import sys
import traceback
import urllib

from game import Game
import domparser
import stringutils
import web


APPLIST_URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
_games = dict()
_applist = web.get_json_data_from_url(APPLIST_URL)
for app in iter(_applist['applist']['apps']['app']):
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


def get_game_info(game, name):
    url          = 'http://store.steampowered.com/app/' + game.store.appid
    status, page = web.get_utf8_web_page(url)

    if (status == 302):
        game.store.description = 'The game is not on steam anymore.'
        print('The page for game {0} redirects somewhere else'
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
              .format(game.name, game.description))
        return

    # middle left column
    game_left_column  = domparser.get_element(document, 'div',
                                              class_='leftcol game_description_column')

    purchase_block    = domparser.get_element(game_left_column, 'div',
                                              id='game_area_purchase')
    game.store.is_dlc = get_game_is_dlc(purchase_block)
    game.store.price  = get_game_price(purchase_block)

    game.store.os     = get_game_os(game_left_column)

    # top right header
    glance_ctn_block  = domparser.get_element(document, 'div',
                                              class_='glance_ctn')
    game.store.image        = get_game_image(glance_ctn_block)
    game.store.avg_review,\
    game.store.cnt_review   = get_game_review(glance_ctn_block)
    game.store.release_date = get_game_release_date(glance_ctn_block)
    game.store.tags         = get_game_tags(glance_ctn_block)
    if (game.store.is_dlc):
        game.store.description  = get_dlc_description(document)
    else:
        game.store.description  = get_game_description(glance_ctn_block)


    # middle right column
    game.store.genres       = get_game_genres(document)
    game.store.details      = get_game_details(document)


    # not parsed from the page
    game.store.link         = url
    price_date              = str(datetime.datetime.now().date())
    game.store.price_date   = ('{0} {1}, {2}'
                         .format(calendar.month_abbr[int(price_date[5:7])],
                                 price_date[8:], price_date[:4]))

    print('Info for game {0} was retrieved, {1}'
          .format(name, str(datetime.datetime.now().time())))


def get_game_image(glance_ctn_block):
    return domparser.get_value(glance_ctn_block, 'img', 'src',
                               class_='game_header_image_full')


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
            return description.strip()

    return None


def get_game_review(glance_ctn_block):
    overall_block = domparser.get_element(
        glance_ctn_block, 'div', class_='subtitle column',
        string='Overall:')

    if (overall_block == None):
        print('None overall_block for game of appid: {0}'.format(appid))
        return '', '0'

    user_reviews_block = domparser.get_parent(overall_block, 'div')

    reviewCount = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='reviewCount')

    ratingValue = domparser.get_value(user_reviews_block, 'meta',
                                      'content', itemprop='ratingValue')

    return ratingValue, reviewCount


def get_game_release_date(glance_ctn_block):
    date = domparser.get_text(glance_ctn_block, 'span',
                              class_='date')
    if (date):
        return date.strip()

    return None


def get_game_is_dlc(purchase_block):
    dlc_block = domparser.get_element(purchase_block, 'div',
                                      class_='game_area_dlc_bubble game_area_bubble')
    return (dlc_block is not None)


def get_game_price(purchase_block):
    discount_price = domparser.get_text(purchase_block, 'div',
                                        class_='discount_final_price')

    if (discount_price):
        return float(discount_price.strip().replace('$', ''))

    prices = domparser.get_texts(purchase_block, 'div',
                               class_='game_purchase_price price')
    for price in prices:
        if (price):
            # we got the wrong div
            if ('demo' in price.lower()):
                continue

            price = price.replace('$', '').strip()
            if (price.replace('.','',1).isdigit()):
                return float(price)
            elif (('free' in price.lower()) or ('play' in price.lower())):
                return 0.00
            else:
                print('Unexpected price: {0}'.format(price))
                return None

    play_game_span = domparser.get_element(purchase_block, 'span',
                                           string='Play Game')

    if (play_game_span):
        return 0.00

    return None


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
                                    id='category_block')
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
        return list(map(lambda s: s.strip(),
                        domparser.get_texts(tags_block, 'a')))
    return list()



# simple test
if __name__ == '__main__':
    game = Game('1001 Spikes')
    game.appid = '260790'
    get_game_info(game)
    print(game.details)
    print(game.tags)
