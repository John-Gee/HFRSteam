#!/usr/bin/python

import aiofiles
import argparse
import asyncio
from datetime import datetime
import logging
import os
import traceback
import uvloop

import bboutput
import gamesinfo
import hfrparser
import htmloutput
import parallelism
import steamlist
import styledprint
import utils
import winelist


class MyFormatter(argparse.ArgumentDefaultsHelpFormatter,
                  argparse.MetavarTypeHelpFormatter):
    def __init__(self, *args, **kwargs):
        super(MyFormatter, self).__init__(*args, max_help_position=100,
                                          width=80, **kwargs)


    def _format_action_invocation(self, action):
        if ((not action.option_strings) or (action.nargs == 0)):
            return super()._format_action_invocation(action)

        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return '{0} {1}'.format(', '.join(action.option_strings),
                                args_string.upper())


def get_parser():
    parser = argparse.ArgumentParser(description=('Parse the HFR list of Steam'
                                     ' games offered, output it to bb/html'),
                                     usage='%(prog)s [options]',
                                     formatter_class=MyFormatter)
    parser.add_argument('-a', '--all', action='store_true', dest='all',
                        help='do not skip nonavailable games')
    parser.add_argument('-c', '--cache-only', action='store_true',
                        dest='cacheonly', help='do not query the store')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        dest='dryrun',help='do not modify anything on disk')
    parser.add_argument('-f', '--fuzzy-matching', action='store_true',
                         dest='fuzzymatching', help='enable fuzzy matching')
    parser.add_argument('-i', '--ignore-cache', action='store_true',
                        dest='ignorecache', help='no read but write to cache')
    parser.add_argument('-l', '--list', dest='liste', type=str, metavar='LIST',
                        help='parse a text list instead of HFR')
    parser.add_argument('-r', '--refresh', dest='game', type=str,
                        help='refresh the games matching the string')
    parser.add_argument('-s', '--skip', dest='skip', action='store_true',
                        help='disable updating the Steam database')
    parser.add_argument('-t', '--threads', dest='threads', default='0',
                        type=int, help='number of parallel threads to use')
    parser.add_argument('-v', '--verbosity', dest='verbosity', default='1',
                        type=int,
                        help='verbosity to use (0: E, 1: W, 2: D)')
    return parser


async def get_applist(options):
    start = datetime.now()
    styledprint.print_info_begin('AppList Refresh')
    applist = await steamlist.refresh_applist(options.dryrun, options.skip, from_scratch=False)
    styledprint.print_info_begin('AppList Refresh Done')
    end   = datetime.now()
    styledprint.print_debug('get_applist took:', (end - start).total_seconds())
    return applist


async def get_wine_ratings():
    start = datetime.now()
    styledprint.print_info_begin('Getting Wine Ratings')
    ratings = await winelist.get_ratings()
    styledprint.print_info_begin('Getting Wine Ratings Done')
    end   = datetime.now()
    styledprint.print_debug('get_wine_ratings took:', (end - start).total_seconds())
    return ratings


async def parse_list(options):
    start = datetime.now()
    styledprint.print_info_begin('Parsing HFR')
    if (options.liste == None):
        games = await hfrparser.parse_hfr()
    else:
        games = await hfrparser.parse_list(options.liste)
    styledprint.print_info_end('Parsing HFR Done')
    end   = datetime.now()
    styledprint.print_debug('parse_list took:', (end - start).total_seconds())
    return games


def write_output_files(options, games):
    OUTPUT_FOLDER = 'docs'
    JS_FILE       = os.path.join(OUTPUT_FOLDER, 'hfr.js')
    BB_FILE       = os.path.join(OUTPUT_FOLDER, 'bb.txt')
    if (not os.path.exists(OUTPUT_FOLDER)):
        os.makedirs(OUTPUT_FOLDER)

    tasks = [asyncio.ensure_future(htmloutput.output_to_js(options.dryrun, games, JS_FILE)),
             asyncio.ensure_future(bboutput.output_to_bb(options.dryrun, games, BB_FILE))]

    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == '__main__':
    logging.basicConfig(filename='mylog.log',
                        filemode = 'w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    #logging.getLogger('').addHandler(console)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    #loop.set_debug(True)
    options    = get_parser().parse_args()
    steamgames = utils.DictCaseInsensitive()
    styledprint.set_verbosity(options.verbosity)
    parallelism.create_pool(8, loop)

    try:
        tasks = [asyncio.ensure_future(get_applist(options)),
                asyncio.ensure_future(get_wine_ratings()),
                asyncio.ensure_future(parse_list(options))]

        loop.run_until_complete(asyncio.gather(*tasks))
        steamgames = tasks[0].result()
        winedb     = tasks[1].result()
        games      = tasks[2].result()

        start = datetime.now()
        gamesinfo.get_games_info(options, games, steamgames, winedb)
        end   = datetime.now()
        styledprint.print_debug('get_games_info took:', (end - start).total_seconds())

        start = datetime.now()
        write_output_files(options, games)
        end   = datetime.now()
        styledprint.print_debug('write_output_files took:', (end - start).total_seconds())

    except Exception as e:
        print(e)
        print(traceback.format_exc())

    parallelism.shutdown_pool(wait=True)
    # this genereates a stack overflow
    # when the loop was previously stopped
    #loop.close()
