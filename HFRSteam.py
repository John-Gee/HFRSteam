#!/usr/bin/python

from optparse import OptionParser
import os
import sys

import output
import hfrparser
import parser


def main():
    usage = "usage: %prog [options] arg"
    optionparser = OptionParser(usage)
    optionparser.add_option("-c", "--cache-only", action="store_true", dest="cacheonly",
                            help="Does not query steam and only work on games in cache")
    optionparser.add_option("-i", "--ignore-cache", action="store_true", dest="ignorecache",
                            help="Ignore the data stored in cache")
    optionparser.add_option("-l", "--list", dest="list",
                            help="Provide a text list to parse instead of parsing HFR")
    optionparser.add_option("-m", "--matching-words", action="store_true", dest="matchingwords",
                            help="Use a word matching algorithm to find a name matching in the steamdb (potentially wrong)")
    optionparser.add_option("-n", "--number-games", dest="number_games",
                            help="Number of games to work on. Only for dev purposes")
    optionparser.add_option("-r", "--refresh-all", action="store_true", dest="refreshall",
                            help="Refresh all games, ignoring the current cache.")
    optionparser.add_option("-R", "--refresh-named", dest="game",
                            help="Refresh the game listed, and all games not in cache")
    optionparser.add_option("-t", "--threads", dest="threads", default="25", type="int",
                            help="Number of parallel threads to use for fetching the steam information.")
    optionparser.add_option("-w", "--wait-on-steam-timeout", action="store_true", dest="waitonsteamtimeout",
                            help="Wait on timeouts. The default behavior is to stop querying Steam.")

    (options, args) = optionparser.parse_args()

    if (options.list == None):
        list  = hfrparser.parse_hfr()
        games = parser.parse_list(list, options)
    else:
        list  = open(options.list, "r")
        games = parser.parse_list(list, options)
        list.close()

    OUTPUT_FOLDER = "docs"
    OUTPUT_FILE   = OUTPUT_FOLDER + "/index.html"
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    output.output_to_html(games, OUTPUT_FILE)

if __name__ == "__main__":
    main()
