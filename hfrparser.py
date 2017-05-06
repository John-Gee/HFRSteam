import os
import re
import sys

import domparser
from game import Game
import stringutils
import web


def get_post(url, postid):
    status, html = web.get_utf8_web_page(url)
    document     = domparser.load_html(html)
    post         = domparser.get_element(document, 'div', id = postid)

    return str(post)


def get_games(liste, requirements):
    striked       = False
    BEGIN_STRIKED = '<strike>'
    END_STRIKED   = '</strike>'
    END_NEW       = '----'

    games               = dict()
    is_new              = (requirements == "Standard")

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
            if (is_new):
                game = Game(is_available, "Nouveauté")
            else:
                game = Game(is_available, requirements)
            games[cleanname] = game
    return games


def get_names_from_post(post, start, end, is_std):
    subpost = stringutils.substringafter(post, start)
    subpost = stringutils.substringbefore(subpost, end)
    cleansubpost = subpost.replace('<br/>', '\r\n')

    cleansubpost = cleansubpost.replace('&amp;', "&")
    cleansubpost = cleansubpost.replace('"', '')
    if (not is_std):
        cleansubpost = re.sub('.*\( *(Uplay|Rockstar Game Social club|GoG|GOG Galaxy|Battlenet|Android|clef Square Enix|Desura|Origin) *\).*', '', 
                              cleansubpost, flags=re.IGNORECASE)
        cleansubpost = re.sub('.*Clef Origin Humble Bundle.*', '', cleansubpost, flags=re.IGNORECASE)
        cleansubpost = re.sub('\(.+\)', '', cleansubpost)
        cleansubpost = re.sub(' *X[0-9] *', '', cleansubpost)
        cleansubpost = re.sub('<strike>X[0-9]</strike>', '', cleansubpost)
        cleansubpost = cleansubpost.replace('****', '')

    cleansubpost = cleansubpost.strip()

    # the separator is \x1c
    return cleansubpost.splitlines()


def parse_hfr_std():
    POST_ID = 'para8945000'
    URL     = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm'
    post    = get_post(URL, POST_ID)

    START = '<strong>Clefs  <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> Steam <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> :</strong> <br/><strong> <br/>'
    END   = '--------------------------------------------------------------------------'

    names = get_names_from_post(post, START, END, True)
    return get_games(names, "Standard")


def parse_hfr_donateur():
    POST_ID = 'para8952242'
    URL     = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm'
    post    = get_post(URL, POST_ID)

    START = '<strong>Liste donateur:</strong>'
    END   = '----'

    names = get_names_from_post(post, START, END, False)
    return get_games(names, "Donateur")


def parse_hfr_premium():
    POST_ID = 'para8952242'
    URL     = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm'
    post    = get_post(URL, POST_ID)

    START = '<strong>Liste Premium ( exclusivement réservée aux donateurs réguliers ):</strong>'
    END   = '----'

    names = get_names_from_post(post, START, END, False)
    return get_games(names, "Premium")

def parse_hfr():
    games         = parse_hfr_std()
    games.update(parse_hfr_donateur())
    games.update(parse_hfr_premium())
    return games

if __name__ == '__main__':
    games = parse_hfr_donateur()
    for game in games:
        print(game)
