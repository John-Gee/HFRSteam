import os
import re
import sys

import domparser
from game import Game
import stringutils
import web


def get_post():
    HFR_URL      = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000'

    status, html = web.get_utf8_web_page(HFR_URL)
    document     = domparser.load_html(html)
    post         = domparser.get_element(document, 'div', id = 'para8945000')

    return str(post)


def get_games(liste):
    striked       = False
    BEGIN_STRIKED = '<strike><span style=color:#FF0000>'
    END_STRIKED   = '</span></strike>'
    END_NEW       = '----'

    games               = dict()
    is_new              = True

    for name in liste:
        if (not name):
            continue
        name = name.strip()

        if (name.startswith(END_NEW)):
            is_new = False
            continue

        if (name.startswith(BEGIN_STRIKED)):
            is_available = False
            if (not name.endswith(END_STRIKED)):
                striked = True
        else:
            if (striked):
                is_available = False
                if (name.endswith(END_STRIKED)):
                    striked = False
            else:
                is_available = True

        cleanname = re.sub('<.*?>', '', name).replace('(+)', '').strip()
        if (cleanname):
            game = Game(is_available, is_new)
            games[cleanname] = game
    return games


def get_names_from_post(post):
    START = '<strong>Clefs  <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> Steam <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> :</strong> <br/><strong> <br/>'
    END   = '--------------------------------------------------------------------------'

    subpost = stringutils.substringafter(post, START)
    subpost = stringutils.substringbefore(subpost, END)

    cleansubpost = subpost.replace('<br/>', '\r\n')
    cleansubpost = cleansubpost.replace('&amp;', "&")
    cleansubpost = cleansubpost.replace('"', '')
    cleansubpost = cleansubpost.strip()

    # the separator is \x1c
    return cleansubpost.splitlines()


def parse_hfr():
    post  = get_post()

    names = get_names_from_post(post)
    return get_games(names)


if __name__ == '__main__':
    parse_hfr()
