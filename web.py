import sys
import urllib.request
import urllib.parse

def get_utf8_web_page(url, cookie=None):
    if (cookie is None):
        f = urllib.request.urlopen(url)
    else:       
        opener = urllib.request.URLopener()
        opener.addheaders.append(('Cookie', cookie))
        f = opener.open(url)
    return f.read().decode('utf-8')
