import os


def output_to_bb(games, file):
    bbcode = ''
    for gameName in sorted(games):
        if (games[gameName].store.link != ''):
            gamecode = '[url={0}]{1}[/url]'.format(
                games[gameName].store.link, gameName)
        else:
            gamecode = gameName
        bbcode = '{0}{1}{2}'.format(bbcode, gamecode, os.linesep)

    f = open(file, 'w')
    f.write(bbcode)
    f.close()
