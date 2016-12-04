import os
import sys
import web

import stringutils


def parse_hfr():
    HFR_URL    = "http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000"

    START      = "<br /><strong>Clefs &nbsp;<img src=\"http://forum-images.hardware.fr/images/perso/icon4.gif\" alt=\"[:icon4]\" title=\"[:icon4]\" /> Steam"
    REAL_START = "<strong>"
    END        = "<br />&nbsp;<br />--------------------------------------------------------------------------"

    page = web.get_utf8_web_page(HFR_URL)
    page = stringutils.substringafter(page, START, 1)
    page = stringutils.substringafter(page, REAL_START, 1)
    page = stringutils.substringbefore(page, END, -1)

    page = page.replace("&nbsp;<br />", "\x1c")
    page = page.replace("&nbsp;", "")
    page = page.replace("&#034;", "")
    page = page.replace("&amp;", "&")
    page = page.replace("<br />", "")
    page = page.replace("----", "")
    page = page.strip()

    # the separator is \x1c
    pages = page.splitlines()
    return pages

if __name__ == "__main__":
    parse_hfr()
