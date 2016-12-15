import os
import sys

import domparser
import stringutils
import web


def get_post():
    HFR_URL    = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000'

    html = web.get_utf8_web_page(HFR_URL)
    document = domparser.load_html(html)
    divSR = domparser.get_element(document, ID = 'para8945000', nodetype = 'div')

    return str(divSR)

def get_list(post):
    HFR_URL    = 'http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000'

    START      = '<strong>Clefs  <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> Steam <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> :</strong> <br/><strong> <br/>'
    END        = '<strong>Clefs  <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> Desura <img alt="[:icon4]" src="http://forum-images.hardware.fr/images/perso/icon4.gif" title="[:icon4]"/> :</strong>'

    subpost = stringutils.substringafter(post, START)
    subpost = stringutils.substringbefore(subpost, END)

    cleansubpost = subpost.replace('<br/>', '\r\n')
    cleansubpost = cleansubpost.replace('&amp;', "&")
    cleansubpost = cleansubpost.replace('"', '')
    cleansubpost = cleansubpost.replace('--', '')
    cleansubpost = cleansubpost.strip()

    # the separator is \x1c
    games = cleansubpost.splitlines()
    games = filter(None, games)

    return games


def parse_hfr():
    post = get_post()
    games = get_list(post)

    return games


if __name__ == "__main__":
    parse_hfr()
