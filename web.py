from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol import heuristics
import logging
import requests
import time


session = requests.Session()
session.headers = {'User-Agent': 'Mozilla/5.0'}
session.cookies = requests.cookies.RequestsCookieJar()
session.cookies.set('birthtime', '1')
session.cookies.set('mature_content', '1')
session.allow_redirects = True

cached_session = CacheControl(session,
                              cache=FileCache('.webcache', forever=True),
                              heuristic=heuristics.ExpiresAfter(days=20),
                              cache_etags=False)


def get_utf8_web_page(url):
    for retry in range(5):
        try:
            logging.debug('About to get the url: ' + url)
            req = cached_session.get(url)
            logging.debug('Got the url: ' + url)
            return req.url, req.status_code, req.text
        except requests.exceptions.TooManyRedirects:
            logging.debug('TooManyRedirects for url: ' + url)
            return None, None, None
        except Exception:
            time.sleep(10)


if __name__ == '__main__':
    url, status, page = get_utf8_web_page(
        'https://forum.hardware.fr/hfr/JeuxVideo/'
        'Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm')
    print(page)
