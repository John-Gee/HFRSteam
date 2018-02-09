#!/usr/bin/python

import argparse
import os

import bboutput
import gamesinfo
import hfrparser
import htmloutput
import utils


def main():
    parser = argparse.ArgumentParser(description=('Parse the HFR list'
                                     'of Steam games offered and convert it to '
                                     'a nice bb/html page.'))
    parser.add_argument('-a', '--all', action='store_true', dest='all',
                        help='Does not skip games that are not available')
    parser.add_argument('-c', '--cache-only', action='store_true', dest='cacheonly',
                        help='Does not query steam and only work on games in cache')
    parser.add_argument('-d', '--dry-run', action='store_true', dest='dryrun',
                        help='Performs a dry run, does not modify anything on disk')
    parser.add_argument('-i', '--ignore-cache', action='store_true', dest='ignorecache',
                        help='Ignore the data stored in cache')
    parser.add_argument('-l', '--list', dest='liste',
                        help='Provide a text list to parse instead of parsing HFR')
    parser.add_argument('-m', '--matching-words', action='store_true', dest='matchingwords',
                        help='Use a word matching algorithm to find a name matching in the steamdb (potentially wrong)')
    parser.add_argument('-n', '--number-games', dest='number_games', type=int,
                        help='Number of games to work on. Only for dev purposes')
    parser.add_argument('-r', '--refresh-named', dest='game',
                        help='Refresh the game listed, and all games not in cache')
    parser.add_argument('-t', '--threads', dest='threads', default='0', type=int,
                        help='Number of parallel threads to use for fetching the steam information.')

    options = parser.parse_args()
    if (options.liste == None):
        games = hfrparser.parse_hfr()
    else:
        f     = open(options.liste, 'r')
        games = utils.DictCaseInsensitive()
        hfrparser.get_games(games, f.read().splitlines(), '')
        f.close()

    gamesinfo.get_games_info(options, games)

    if (options.dryrun):
        return

    OUTPUT_FOLDER = 'docs'
    HTML_FILE     = os.path.join(OUTPUT_FOLDER, 'index.html')
    BB_FILE       = os.path.join(OUTPUT_FOLDER, 'bb.txt')
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    htmloutput.output_to_html(games, HTML_FILE)
    bboutput.output_to_bb(games, BB_FILE)


if __name__ == '__main__':
    main()
