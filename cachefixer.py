#!/usr/bin/python


import cache
import game
import styledprint

def main():

    cachedgames = cache.retrieve_db_from_cache()
    i = 0
    for name in iter(cachedgames):
        game = cachedgames[name]
        if (game.store.link and (game.store.link[len(game.store.link) -1] == '/')):
            game.store.link = game.store.link.strip('/')
            styledprint.print_info('Slash removed from the link')
            i = i + 1
    styledprint.print_info('{0} games cleaned'.format(i))
    cache.save_to_cache(cachedgames)


if __name__ == '__main__':
    main()
