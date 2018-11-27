import asyncio
from datetime import datetime
import re
import uvloop

import domparser
from game import Category, Game
import stringutils
import utils
import web


async def get_document(url):
    async with web.Session(limit_per_host=10) as webSession:
        _, _, html = await webSession.get_web_page(url)
    return domparser.load_html(html)


def get_post(document, postid):
    return domparser.get_element_string(document, 'div', id=postid)


def get_games(games, liste, requirements):
    BEGIN_STRIKED = '<strike>'
    END_STRIKED   = '</strike>'
    BEGIN_NEW     = '<strong>'
    END_NEW       = '</strong>'

    is_new        = False
    ignore        = False
    striked       = False
    basename      = ''

    for name in liste:
        # ignore lines including icon4.gif
        if ((not name) or ('icon4.gif' in name) or (re.match('----', name))):
            continue
        ignore_list = ['humble bundle', 'uplay', 'rockstar game social club',
                        'gog', 'battlenet', 'android', 'square enix', 'desura', 'origin']
        if any(word in name.lower() for word in ignore_list):
            ignore = True
            continue

        name = name.strip()
        if (name.startswith(BEGIN_NEW)):
            is_new = True

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

        if (is_new):
            game = Game(is_available, requirements, True, datetime.now())
        else:
            game = Game(is_available, requirements)
        if (name.endswith(END_NEW)):
            is_new = False

        cleanname = re.sub('<.*?>', '', name).replace('(+)', '')
        cleanname = re.sub('\( .+ *\)', '', cleanname).strip()
        if (cleanname):
            if ('(+)' not in name):
                basename = cleanname
            else:
                if ((basename) and (basename.split(' ')[0] not in cleanname)):
                    cleanname = '{0} {1}'.format(basename, cleanname)
                game.store.category = Category.DLC
                if (ignore):
                    continue

            if ((cleanname not in games) or
                ((not games[cleanname].hfr.is_available) and (is_available))):
                games[cleanname] = game


def get_names_from_post(post, start, end, is_std):
    subpost = stringutils.substringafter(post, start)
    subpost = stringutils.substringbefore(subpost, end)
    cleansubpost = subpost.replace('<br />', '\r\n')
    cleansubpost = cleansubpost.replace('<br></br>', '\r\n')

    cleansubpost = cleansubpost.replace('&amp;', "&")
    cleansubpost = cleansubpost.replace('"', '')
    if (not is_std):
        cleansubpost = re.sub(' *X[0-9] *', '', cleansubpost)
        cleansubpost = re.sub('<strike>X[0-9]</strike>', '', cleansubpost)
        cleansubpost = cleansubpost.replace('****', '')

    cleansubpost = cleansubpost.strip()

    # the separator is \x1c
    return cleansubpost.splitlines()


def parse_hfr_std(games, document):
    POST_ID = 'para8945000'
    post    = get_post(document, POST_ID)

    START = '<strong>Clefs  <img src="https://forum-images.hardware.fr/images/perso/icon4.gif" alt="[:icon4]" title="[:icon4]" /> Steam <img src="https://forum-images.hardware.fr/images/perso/icon4.gif" alt="[:icon4]" title="[:icon4]" /> :</strong>'
    END   = '--------------------------------------------------------------------------'

    names = get_names_from_post(post, START, END, True)
    get_games(games, names, "Standard")


def parse_hfr_donateur_and_premium(games, document):
    POST_ID = 'para8952242'
    post    = get_post(document, POST_ID)

    #donateur
    START = '<strong>Liste donateur:</strong>'
    END   = '----'
    names = get_names_from_post(post, START, END, False)
    get_games(games, names, "Donateur")

    #premium
    START = '<strong>Liste Premium ( exclusivement réservée aux donateurs réguliers ):</strong>'
    END   = '----'
    names = get_names_from_post(post, START, END, False)
    get_games(games, names, "Premium")


async def parse_hfr(games):
    URL      = 'https://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm'
    document = await get_document(URL)
    parse_hfr_std(games, document)
    parse_hfr_donateur_and_premium(games, document)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    games = {}
    tasks = [asyncio.ensure_future(parse_hfr(games))]
    loop.run_until_complete(asyncio.gather(*tasks))
    print(len(games))
