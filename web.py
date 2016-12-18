import json
import requests
import sys


def get_utf8_web_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('birthtime', '1')
    jar.set('mature_content', '1')
    req = requests.get(url, headers=headers, params=jar, cookies=jar)

    return req.text


def get_json_data_from_url(url):
    return json.loads(get_utf8_web_page(url))
