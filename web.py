import json
import requests


session = requests.Session()


def get_utf8_web_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('birthtime', '1')
    jar.set('mature_content', '1')
    req = session.get(url, headers=headers, cookies=jar, allow_redirects=False)
    return req.status_code, req.text


def get_json_data_from_url(url):
    status, page = get_utf8_web_page(url)
    return json.loads(page)
