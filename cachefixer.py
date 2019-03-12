#!/usr/bin/python


from cache import Cache
import game
import styledprint

import os

def main():

    CACHE_PATH      = os.path.join('cache', 'games.p')
    cache           = Cache(CACHE_PATH)
    cachedgames = cache.load_from_cache()
    i = 0
    for name in iter(cachedgames):
        game = cachedgames[name]
        if (not hasattr(game, 'wine')):
            game.wine = None
            i = i + 1
    styledprint.print_info('{0} games cleaned'.format(i))
    cache.save_to_cache(cachedgames)


if __name__ == '__main__':
    main()
