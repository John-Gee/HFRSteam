import json
import sys
import urllib.request


def get_utf8_web_page(url, cookie=None):
    if (cookie is None):
        f = urllib.request.urlopen(url)
    else:
        opener = urllib.request.URLopener()
        opener.addheaders.append(('Cookie', cookie))
        f = opener.open(url)
    return f.read().decode('utf-8')


def get_json_data_from_url(url):
    f = urllib.request.urlopen(url)
    return json.loads(f.read().decode('utf-8'))
