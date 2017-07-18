#!/usr/bin/python

from optparse import OptionParser
import os

import bboutput
import gamesinfo
import hfrparser
import htmloutput


def main():
    usage = 'usage: %prog [options] arg'
    optionparser = OptionParser(usage)
    optionparser.add_option('-a', '--all', action='store_true', dest='all',
                            help='Does not skip games that are not available')
    optionparser.add_option('-c', '--cache-only', action='store_true', dest='cacheonly',
                            help='Does not query steam and only work on games in cache')
    optionparser.add_option('-i', '--ignore-cache', action='store_true', dest='ignorecache',
                            help='Ignore the data stored in cache')
    optionparser.add_option('-m', '--matching-words', action='store_true', dest='matchingwords',
                            help='Use a word matching algorithm to find a name matching in the steamdb (potentially wrong)')
    optionparser.add_option('-n', '--number-games', dest='number_games',
                            help='Number of games to work on. Only for dev purposes')
    optionparser.add_option('-r', '--refresh-named', dest='game',
                            help='Refresh the game listed, and all games not in cache')
    optionparser.add_option('-t', '--threads', dest='threads', default='0', type='int',
                            help='Number of parallel threads to use for fetching the steam information.')
    optionparser.add_option('-w', '--wait-on-steam-timeout', action='store_true', dest='waitonsteamtimeout',
                            help='Wait on timeouts. The default behavior is to stop querying Steam.')

    (options, args) = optionparser.parse_args()

    games = hfrparser.parse_hfr()

    gamesinfo.get_games_info(options, games)
    OUTPUT_FOLDER = 'docs'
    HTML_FILE     = OUTPUT_FOLDER + '/index.html'
    BB_FILE       = OUTPUT_FOLDER + '/bb.txt'
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    htmloutput.output_to_html(games, HTML_FILE)
    bboutput.output_to_bb(games, BB_FILE)


if __name__ == '__main__':
    main()
