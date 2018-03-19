import aiofiles
import os


async def output_to_bb(dryrun, games, path):
    bbcode = ''
    requirements = ''
    # sort first by name, then by is_new and finally by requirements
    # each following sorts keeps the previous one intact as much as possible
    for gameName, game in sorted(
        games.items(), key = lambda x:
            (x[1].hfr.requirements, not x[1].hfr.is_new, x[0].lower())):
        if (not game.hfr.is_available):
            continue

        newbbcode = ''

        if (game.store.link != ''):
            newbbcode = '{0}[url={1}]{2}[/url]'.format(
                newbbcode, game.store.link, gameName)
        else:
            newbbcode = '{0}{1}'.format(
                newbbcode, gameName)

        if (game.hfr.is_new):
            newbbcode = '[b]{0}[/b]'.format(newbbcode)

        newbbcode = '{0}{1}'.format(newbbcode, os.linesep)

        if (game.hfr.requirements != requirements):
            requirements = game.hfr.requirements
            newbbcode = '{0}[b]{1}:[/b]{0}{2}'.format(
                os.linesep, requirements, newbbcode)

        bbcode = '{0}{1}'.format(bbcode, newbbcode)

    if (not dryrun):
        async with aiofiles.open(path, 'w', encoding='utf8') as f:
            await f.write(bbcode.strip())
