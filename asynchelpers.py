import asyncio


def sync(fn, *args, **kwargs):
    try:
        loop = asyncio.get_event_loop()
    except Exception as e:
        print(type(e))
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(fn(*args, **kwargs))
