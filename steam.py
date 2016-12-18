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


def getshortdescription(longdesc):
    if (longdesc == None):
        return longdesc

    MAX_LENGTH = 400

    cleandesc = longdesc.replace("\"", "").replace(
        os.linesep, " ").replace("\r", " ")
    cleandesc = re.sub("<br.?.?>", " ", cleandesc)
    cleandesc = re.sub("<.*?>", "", cleandesc)
    cleandesc = re.sub(" +", " ", cleandesc)

    if (len(cleandesc) > MAX_LENGTH):
        shortdesc = stringutils.rsubstringbefore(
            cleandesc[:MAX_LENGTH], " ") + " [...]"
        return shortdesc

    return cleandesc


def get_appinfo(appid):
    APPDETAIL_URL = "http://store.steampowered.com/api/appdetails?appids="

    return web.get_json_data_from_url(APPDETAIL_URL + appid)


def get_game_info(game):
    return get_game_info_from_api(game)


def get_game_info_from_api(game):
    arewebanned = False
    # purely to reduce the following lines length
    appid       = game.appid
    try:
        game.avg_review, game.cnt_review = get_review_from_steam(appid)

        info = get_appinfo(appid)
        if ("data" in info[appid]) and (len(info[appid]["data"]) > 0):

            if (len(info[appid]["data"]["short_description"]) > 0):
                game.description = getshortdescription(
                    info[appid]["data"]["short_description"])
            elif (len(info[appid]["data"]["about_the_game"]) > 0):
                game.description = getshortdescription(
                    info[appid]["data"]["about_the_game"])
            else:
                game.description = getshortdescription(
                    info[appid]["data"]["detailed_description"])

            game.image = info[appid]["data"]["header_image"]

            if (("type" in info[appid]["data"]) and (info[appid]["data"]["type"].lower() == "dlc")):
                game.is_dlc = "1"

            if (len(info[appid]["data"]["linux_requirements"]) > 0):
                game.os.append("Linux")
            if (len(info[appid]["data"]["mac_requirements"]) > 0):
                game.os.append("Mac")
            if (len(info[appid]["data"]["pc_requirements"]) > 0):
                game.os.append("Windows")

            if (info[appid]["data"]["is_free"]):
                game.price = 0.00
            elif (("price_overview" in info[appid]["data"]) and (len(info[appid]["data"]["price_overview"]) > 0)):
                game.price = (info[appid]["data"][
                    "price_overview"]["final"]) / 100
            elif ((len(info[appid]["data"]["package_groups"]) > 0) and (info[appid]["data"]["package_groups"][0]["subs"][0]["price_in_cents_with_discount"] >= 0)):
                game.price = (info[appid]["data"]["package_groups"][0][
                    "subs"][0]["price_in_cents_with_discount"]) / 100
            else:
                game.price = None

            if ((game.price != None) and (game.price > 60)):
                print("The price of game " + game.name +
                    ": " + price + " is suspicious.")

            price_date = str(datetime.datetime.now().date())
            game.price_date = calendar.month_abbr[
                int(price_date[5:7])] + " " + price_date[8:] + ", " + price_date[:4]

            if ("genres" in info[appid]["data"]):
                for genre in iter(info[appid]["data"]["genres"]):
                    game.genres.append(genre["description"])

            game.release_date = info[appid][
                "data"]["release_date"]["date"]

            game.link = "http://store.steampowered.com/app/" + appid

            print("Info for game " + game.name + " was retrieved" +
                  ", " + str(datetime.datetime.now().time()))

        else:
            game.description = "The game is not on steam anymore"

    except urllib.error.HTTPError as err:
        if (repr(err).find("302")):
            game.description = "The game is in the db but not on steam anymore"
        else:
            arewebanned = true

    except:
        print("something failed for game: " + game.name + " appid: " +
              game.appid + ", " + str(datetime.datetime.now().time()))
        traceback.print_exc()

    return arewebanned


def get_review_from_steam(appid):
    APP_URL = 'http://store.steampowered.com/app/'

    page       = web.get_utf8_web_page(APP_URL + appid)

    if ('No user reviews' in page):
        return '', '0'

    document = domparser.load_html(page)

    sorry_block = domparser.get_element(document, 'h2',
        class_ = 'pageheader', string = 'Oops, sorry!')

    if (sorry_block):
        print('An error has occured, the game for appid ' +
              appid + ' has no page.')
        return "", ""

    overall_block = domparser.get_element(
        document, 'div', class_ = 'subtitle column',
        string = 'Overall:')

    if (overall_block == None):
        print('None overall_block for game of appid: ' + appid)
        return '', ''

    user_reviews_block = domparser.get_parent(overall_block, 'div')

    reviewCount = domparser.get_value(user_reviews_block, 'meta',
        'content', itemprop = 'reviewCount')

    ratingValue = domparser.get_value(user_reviews_block, 'meta',
        'content', itemprop = 'ratingValue')

    return ratingValue, reviewCount


def get_list_of_games():
    return _games.keys()
