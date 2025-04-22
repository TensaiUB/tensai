from rich import print
from fakeredis import aioredis as fake_aioredis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from tensai import utils
from tensai.bot_core import BotManager

import asyncio

git_info = asyncio.run(utils.get_git_info())

print(f"""[sky_blue1] _____                    _ 
|_   _|__ _ __  ___  __ _(_)
  | |/ _ \ '_ \/ __|/ _` | |
  | |  __/ | | \__ \ (_| | |
  |_|\___|_| |_|___/\__,_|_|

Commit: #{git_info['last_commit_short']}
Github: https://github.com/TensaiUB/tensai[/sky_blue1]
""")

async def get_redis():
    try:
        redis_client = Redis(
            host="localhost",
            port=6379,
            password=None,
            decode_responses=True
        )
        await redis_client.ping()
        print("[green]✅ Connected to Redis[/green]")
        return redis_client
    except (ConnectionError, RedisError, OSError):
        print("[green]✅ Connected to fake Redis[/green]")
        return await fake_aioredis.FakeRedis(decode_responses=True)

redis = asyncio.run(get_redis())

manager = BotManager()
bot, dp = manager.load()