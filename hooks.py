from asyncio import sleep, ensure_future, Future
from datetime import datetime
from typing import List

from aiogram import Dispatcher
from tortoise import Tortoise

from db import Mentions, init_db

__all__ = ['startup', 'shutdown']
periodic_tasks: List[Future] = []


async def enable_mentions():
    await sleep(10)

    while True:
        now = datetime.utcnow().date()
        await Mentions.filter(enable_after__gte=now).update(enable_after=None, is_enabled=True)
        await sleep(3600)


async def startup(db: Dispatcher):
    await init_db()
    periodic_tasks.append(ensure_future(enable_mentions()))


async def shutdown(db: Dispatcher):
    for fut in periodic_tasks:
        fut.cancel()

    await Tortoise.close_connections()
