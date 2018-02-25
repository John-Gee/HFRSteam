from cachecontrol import CacheControl
import requests


session        = requests.Session()
cached_session = CacheControl(session)


def get_utf8_web_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('birthtime', '1')
    jar.set('mature_content', '1')
    try:
        req = cached_session.get(url, headers=headers,
                                 cookies=jar, allow_redirects=True)
        return req.url, req.status_code, req.text
    except requests.exceptions.TooManyRedirects:
        return None, None, None


if __name__ == '__main__':
    url, status, page = get_utf8_web_page(
        'https://forum.hardware.fr/hfr/JeuxVideo/'
        'Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm')
    print(page)
