import aiohttp
import asyncio
import datetime
import logging
import random
import time
import traceback

import asynchelpers
import styledprint


class Session():
    def create(self, timeout):
        minver = str(random.randint(0,5))
        self.aiohttp = aiohttp.ClientSession(headers={'User-Agent':
                                                          'Mozilla/5.0' + minver},
                                             cookies={'birthtime': '1',
                                                      'mature_content': '1'},
                                             read_timeout=timeout,
                                             connector=aiohttp.TCPConnector(limit=50,
                                                                            ttl_dns_cache=600))


    def get(self, *args, **kwargs):
        try:
            return self.aiohttp.get(*args, **kwargs,
                                    allow_redirects=True)
        except Exception as e:
            styledprint.print_error('An error happened in aiohttp.get: ', e)
            styledprint.print_error(traceback.format_exc())
            raise e


    def head(self, *args, **kwargs):
        try:
            return self.aiohttp.head(*args, **kwargs,
                                     allow_redirects=True)
        except Exception as e:
            styledprint.print_error('An error happened in aiohttp.head: ', e)
            styledprint.print_error(traceback.format_exc())
            raise e


    def close(self):
        asynchelpers.sync(self.aiohttp.close)


session = Session()


def create_session(timeout=300):
    session.create(timeout)


def close_session():
    session.close()


beforesleep = datetime.datetime.utcnow() + datetime.timedelta(days=1)

async def get_web_page(url, badurl=None):
    global beforesleep
    for retry in range(200):
        try:
            await asyncio.sleep(random.randint(10,59)/10000)
            logging.debug('About to get the url: {}, {}'
                            .format(url, str(datetime.datetime.now())))
            async with session.get(url) as resp:
                logging.debug('Got the url: {} {}'
                                .format(url, str(datetime.datetime.now())))
                if (len(resp.history) >= 10):
                    logging.debug('TooManyRedirects for url: ' + url)
                    return None, None, None
                if (resp.status == 200):
                    sURL = str(resp.url)
                    if ((badurl) and (sURL == badurl)):
                        logging.debug('url {} redirected to badurl {}'
                                      .format(url, badurl))
                        return sURL, resp.status, None
                    text = await resp.text()
                    return sURL, resp.status, text
                elif (resp.status in [403, 429]):
                    logging.debug('HTTP status is {} for: {}, retrying!'
                                  .format(resp.status, resp.url))
                    respdate = datetime.datetime.strptime(resp.headers['date'],
                                                          '%a, %d %b %Y %X %Z')
                    diff     = (respdate - beforesleep).total_seconds()
                    if (diff <= 1):
                        beforesleep = datetime.datetime.utcnow()
                        logging.debug('sleep not yet done, sleeping')
                        #time.sleep(5 * retry)
                        time.sleep(min(5 * retry, 120))
                elif (resp.status in [408, 500, 502, 503, 504]):
                    logging.debug('HTTP status is {} for: {}, retrying!'.format(resp.status, resp.url))
                    await asyncio.sleep(0.001 * retry)
                else:
                    raise Exception('HTTP status is {} for: {}, not retrying'.format(resp.status, resp.url))
                    #return None, None, None

        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            logging.debug('get_utf8_web_page got {} for url {}, retrying'.format(type(e), url))
            await asyncio.sleep(0.002 * retry)
        except (aiohttp.client_exceptions.ServerDisconnectedError, ) as e:
            logging.debug('get_utf8_web_page got {} for url {}'.format(type(e), url))
            #await asyncio.sleep(1 * retry)
            await asyncio.sleep(5)

    raise Exception('Get did not worked even after many retries for url', url)


if __name__ == '__main__':
    url, status, page = get_utf8_web_page(
        'https://forum.hardware.fr/hfr/JeuxVideo/'
        'Achat-Ventes/gratuit-origin-download-sujet_171605_1.htm')
    print(page)
