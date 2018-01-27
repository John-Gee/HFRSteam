import os


def output_to_bb(games, file):
    bbcode = ''
    requirements = ''
    for gameName, game in sorted(
        games.items(), key = lambda x: (x[1].hfr.requirements, x[0])):
        if (not game.hfr.is_available):
            continue

        if (game.hfr.requirements != requirements):
            requirements = game.hfr.requirements
            bbcode = '{0}{1}[b]{2}:[/b]{1}'.format(
                bbcode, os.linesep, requirements, os.linesep)

        if (game.store.link != ''):
            bbcode = '{0}[url={1}]{2}[/url]{3}'.format(
                bbcode, game.store.link, gameName, os.linesep)
        else:
            bbcode = '{0}{1}{2}'.format(
                bbcode, gameName, os.linesep)

    f = open(file, 'w', encoding='utf8')
    f.write(bbcode)
    f.close()
