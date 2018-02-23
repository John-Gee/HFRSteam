#!/usr/bin/python

import argparse
import os

import bboutput
import gamesinfo
import hfrparser
import htmloutput
import utils


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
    parser = argparse.ArgumentParser(description=('Parses the HFR list of Steam games'
                                     ' offered and convert it to bb/html.'''),
                            usage='%(prog)s [options]',
                            formatter_class=MyFormatter,)
    parser.add_argument('-a', '--all', action='store_true', dest='all',
                        help='do not skip nonavailable games')
    parser.add_argument('-c', '--cache-only', action='store_true', dest='cacheonly',
                        help='do not query the store, cache-only')
    parser.add_argument('-d', '--dry-run', action='store_true', dest='dryrun',
                        help='do not modify anything on disk')
    parser.add_argument('-i', '--ignore-cache', action='store_true', dest='ignorecache',
                        help='do not read the cache, but write to it')
    parser.add_argument('-l', '--list', dest='liste', type=str, metavar='LIST',
                        help='parse a text list instead of HFR')
    parser.add_argument('-m', '--matching-words', action='store_true', dest='matchingwords',
                        help='use approximate string matching')
    parser.add_argument('-r', '--refresh', dest='game', type=str,
                        help='refresh the games matching the string')
    parser.add_argument('-t', '--threads', dest='threads', default='0', type=int,
                        help='number of parallel threads to use')
    return parser


def parse_list(options):
    if (options.liste == None):
        games = hfrparser.parse_hfr()
    else:
        games = utils.DictCaseInsensitive()
        with open(options.liste, 'r') as f:
            hfrparser.get_games(games, f.read().splitlines(), '')
    return games


def write_output_files(games):
    OUTPUT_FOLDER = 'docs'
    HTML_FILE     = os.path.join(OUTPUT_FOLDER, 'index.html')
    BB_FILE       = os.path.join(OUTPUT_FOLDER, 'bb.txt')
    if (not os.path.exists(OUTPUT_FOLDER)):
        os.makedirs(OUTPUT_FOLDER)
    htmloutput.output_to_html(games, HTML_FILE)
    bboutput.output_to_bb(games, BB_FILE)


if __name__ == '__main__':
    options = get_parser().parse_args()
    games   = parse_list(options)

    gamesinfo.get_games_info(options, games)

    if (options.dryrun):
        sys.exit(0)

    write_output_files(games)
