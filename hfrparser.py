import sys
import os
import web
import stringutils

def parse_hfr():
    url = "http://forum.hardware.fr/hfr/JeuxVideo/Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm#t8945000"
    
    start      = "<br /><strong>Clefs &nbsp;<img src=\"http://forum-images.hardware.fr/images/perso/icon4.gif\" alt=\"[:icon4]\" title=\"[:icon4]\" /> Steam"
    #real_start = "<br />----"
    real_start = "<strong>"
    end        = "<br />&nbsp;<br />--------------------------------------------------------------------------"
    
    page = web.get_utf8_web_page(url)
    page = stringutils.substringafter(page, start, 1)
    page = stringutils.substringafter(page, real_start, 1)
    page = stringutils.substringbefore(page, end,-1)
    
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
