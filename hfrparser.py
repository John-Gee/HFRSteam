import os
import re
import sys

import domparser
import stringutils
import web


def get_post():
    HFR_URL      = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000'

    status, html = web.get_utf8_web_page(HFR_URL)
    document     = domparser.load_html(html)
    post         = domparser.get_element(document, 'div', id = 'para8945000')

    return str(post)


def clean_list(games):
    striked       = False
    BEGIN_STRIKED = '<strike><span style=color:#FF0000>'
    END_STRIKED   = '</span></strike>'
    END_NEW       = '----'

    newgames         = list()
    numberofnewgames = 0
    i                = 0

    for game in games:
        if (not game):
            continue
        game = game.strip()

        if (game.startswith(END_NEW)):
            numberofnewgames = i
            continue

        if (game.startswith(BEGIN_STRIKED)):
            if (not game.endswith(END_STRIKED)):
                striked = True
                game    += END_STRIKED
        else:
            if (striked):
                if (game.endswith(END_STRIKED)):
                    striked = False
                else:
                    game    += END_STRIKED
                game = BEGIN_STRIKED + game

        if (re.sub('<.*?>', '', game).strip()):
            newgames.append(game)
            i = i + 1

    return newgames, numberofnewgames


def get_list(post):
    START = '<strong>Clefs  <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> Steam <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> :</strong> <br/><strong> <br/>'
    END   = '--------------------------------------------------------------------------'

    subpost = stringutils.substringafter(post, START)
    subpost = stringutils.substringbefore(subpost, END)

    cleansubpost = subpost.replace('<br/>', '\r\n')
    cleansubpost = cleansubpost.replace('&amp;', "&")
    cleansubpost = cleansubpost.replace('"', '')
    cleansubpost = cleansubpost.strip()

    # the separator is \x1c
    games = cleansubpost.splitlines()
    return clean_list(games)


def parse_hfr():
    post  = get_post()

    # this returns both the list of games and the number of new games
    # maybe in the future we should start creating the game structures here
    return get_list(post)


if __name__ == '__main__':
    parse_hfr()
