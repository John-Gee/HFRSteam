import json
import sys
import urllib.request


def get_utf8_web_page(url, cookie=None):
    if (cookie is None):
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
    else:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie})
    return urllib.request.urlopen(req).read().decode('utf-8')


def get_json_data_from_url(url):
    return json.loads(get_utf8_web_page(url))
