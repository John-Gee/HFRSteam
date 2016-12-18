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


APPLIST_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
_games = dict()
_applist = web.get_json_data_from_url(APPLIST_URL)
for app in iter(_applist["applist"]["apps"]["app"]):
    name = app["name"].lower()
    if (name not in _games):
        _games[name] = app["appid"]


def get_appid(name):
    cleanname = name.lower()
    if (cleanname in _games):
        return _games[cleanname]
    else:
        return ""


def get_list_of_games():
    return _games.keys()


def get_game_info(game):
    url  = 'http://store.steampowered.com/app/' + game.appid
    page = web.get_utf8_web_page(url)

    document = domparser.load_html(page)

    sorry_block = domparser.get_element(document, 'h2',
                                        class_='pageheader',
                                        string='Oops, sorry!')

    if (sorry_block):
        print('An error has occured, the game for appid ' +
              appid + ' has no page.')
        return "", ""

    # top right header
    glance_ctn_block  = domparser.get_element(document, 'div',
                                              class_='glance_ctn')
    game.image        = get_game_image(glance_ctn_block)
    game.description  = get_game_description(glance_ctn_block)
    game.avg_review,\
    game.cnt_review   = get_game_review(glance_ctn_block)
    game.release_date = get_game_release_date(glance_ctn_block)


    # middle left column
    game_left_column  = domparser.get_element(document, 'div',
                                              class_='leftcol game_description_column')

    purchase_block    = domparser.get_element(game_left_column, 'div',
                                              id='game_area_purchase')
    game.is_dlc       = get_game_is_dlc(purchase_block)
    game.price        = get_game_price(purchase_block)

    game.os           = get_game_os(game_left_column)


    # middle right column
    game.genres       = get_game_genres(document)


    # not parsed from the page
    game.link         = url
    price_date        = str(datetime.datetime.now().date())
    game.price_date   = (calendar.month_abbr[int(price_date[5:7])] +
                        " " + price_date[8:] + ", " + price_date[:4])


def get_game_image(glance_ctn_block):
    return domparser.get_value(glance_ctn_block, 'img', 'src',
                               class_='game_header_image_full')


def get_game_description(glance_ctn_block):
    return domparser.get_text(glance_ctn_block, 'div',
                              class_='game_description_snippet')


def get_game_review(glance_ctn_block):
    overall_block = domparser.get_element(
        glance_ctn_block, 'div', class_='subtitle column',
        string='Overall:')

    if (overall_block == None):
        print('None overall_block for game of appid: ' + appid)
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
    return date.strip()


def get_game_is_dlc(purchase_block):
    dlc_block = domparser.get_element(purchase_block, 'div',
                                      class_='game_area_dlc_bubble game_area_bubble')
    # for now we expect the value in a string numerical form
    return str(int(dlc_block is not None))


def get_game_price(purchase_block):
    discount_price = domparser.get_text(purchase_block, 'div',
                                        class_='discount_final_price')

    if (discount_price):
        return discount_price.strip()

    price = domparser.get_text(purchase_block, 'div',
                               class_='game_purchase_price price')

    if (price):
        if ('Free To Play' in price):
            return 0.00
        return float(price.strip().replace("$", ""))

    return None


def get_game_os(game_left_column):
    os = domparser.get_text(game_left_column, 'div', class_='sysreq_tabs')
    os = os.replace('SteamOS + ', '').strip()
    os =  list(map(str.strip, os.split('\r\n')))
    os.sort()
    return os

def get_game_genres(document):
    genre_title = domparser.get_element(document, 'b', string='Genre:')
    return domparser.get_next_siblings_text(genre_title, 'a')