import asyncio
import tqdm


async def progress_bar(tasks):
    for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        if (f):
            await f
