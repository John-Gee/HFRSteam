import requests


session = requests.Session()

def get_utf8_web_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('birthtime', '1')
    jar.set('mature_content', '1')
    try:
        req = session.get(url, headers=headers, cookies=jar, allow_redirects=True)
        return req.url, req.status_code, req.text
    except requests.exceptions.TooManyRedirects:
        return None, None, None
