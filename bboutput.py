import os


def output_to_bb(games, file):
    bbcode = ''
    for gameName in sorted(games):
        if (not games[gameName].hfr.is_available):
            continue

        if (games[gameName].store.link != ''):
            bbcode = '{0}[url={1}]{2}[/url]{3}'.format(
                bbcode, games[gameName].store.link, gameName, os.linesep)
        else:
            bbcode = '{0}{1}{2}'.format(bbcode, gameName, os.linesep)

    f = open(file, 'w', encoding='utf8')
    f.write(bbcode)
    f.close()
