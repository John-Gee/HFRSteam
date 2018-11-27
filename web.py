import aiohttp
import asyncio
import datetime
import logging
import random
import time
import traceback
import uvloop

import asynchelpers
import styledprint


class Session():
    def __init__(self, timeout=300, limit_per_host=100):
        self.beforesleep = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.aiohttp     = aiohttp.ClientSession(headers={'User-Agent':
                                                          'Mozilla/5.0' + str(random.randint(0,5))},
                                                 cookies={'birthtime': '1',
                                                          'mature_content': '1'},
                                                 read_timeout=timeout,
                                                 connector=aiohttp.TCPConnector(
                                                     limit_per_host=limit_per_host,
                                                     ttl_dns_cache=600))

    async def __aenter__(self):
        return self


    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close()


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


    async def get_web_page(self, url, badurl=None):
        for retry in range(200):
            try:
                #await asyncio.sleep(random.randint(10,59)/10000)
                logging.debug('About to get the url: {}, {}'
                                .format(url, str(datetime.datetime.now())))
                async with self.get(url) as resp:
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
                        try:
                            text = await resp.text()
                        except UnicodeDecodeError:
                            text = 'Error decoding the page'
                        return sURL, resp.status, text
                    elif (resp.status in [403, 429]):
                        logging.debug('HTTP status is {} for: {}, retrying!'
                                    .format(resp.status, resp.url))
                        respdate = datetime.datetime.strptime(resp.headers['date'],
                                                            '%a, %d %b %Y %X %Z')
                        diff     = (respdate - self.beforesleep).total_seconds()
                        if (diff <= 1):
                            self.beforesleep = datetime.datetime.utcnow()
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
            except:
                logging.debug('Problematic url in web: ' + url)
                #raise

        raise Exception('Get did not work even after many retries for url', url)


    def close(self):
        return self.aiohttp.close()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    session = Session()
    tasks = [asyncio.ensure_future(session.get_web_page(
        'https://store.steampowered.com/app/964300'))]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.run_until_complete(session.close())
    url, status, page = tasks[0].result()
    print(page)
