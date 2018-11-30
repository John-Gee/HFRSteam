from aiocache import cached, RedisCache
from aiocache.serializers import PickleSerializer
import asyncio


# Taken from aiocache at https://github.com/argaen/aiocache/
# Copyright (c) 2016, Manuel Miranda de Cid
# License at https://github.com/argaen/aiocache/blob/master/LICENSE.txt
def key_from_args(func, args, kwargs):
    ordered_kwargs = sorted(kwargs.items())
    return (
        (func.__module__ or "")
        + func.__name__
        + str(args)
        + str(ordered_kwargs)
    )


class Cor():
    def __init__(self):
        self.cache = RedisCache(serializer=PickleSerializer(),
                                port=6379, timeout=0)


    async def cached(self, cor, *args, ttl=604800, **kwargs):
        key = key_from_args(cor, args, kwargs)
        result = await self.cache.get(key)
        if (result is not None):
            return result
        result = await cor(*args)
        await self.cache.set(key, result, ttl=ttl)
        return result


    async def close(self):
        await self.cache.close()


if __name__ == '__main__':
    async def test(a):
        return a * a

    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(test(2))]
    loop.run_until_complete(asyncio.gather(*tasks))
    res = tasks[0].result()
    print(res)
    cor = Cor()
    tasks = [asyncio.ensure_future(cor.cached(test, 2, ttl=5))]
    loop.run_until_complete(asyncio.gather(*tasks))
    res = tasks[0].result()
    print(res)
    tasks = [asyncio.ensure_future(cor.cached(test, 2, ttl=5))]
    loop.run_until_complete(asyncio.gather(*tasks))
    res = tasks[0].result()
    print(res)
