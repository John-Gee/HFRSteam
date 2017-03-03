import os
import sys


def output_to_bb(games, file):
    bbcode = ''
    for gameName in sorted(games):
        if (games[gameName].store.link != ''):
            bbcode = bbcode + '[url={0}]{1}[/url]{2}'.format(
                games[gameName].store.link, gameName, os.linesep)

    f = open(file, 'w')
    f.write(bbcode)
    f.close()
