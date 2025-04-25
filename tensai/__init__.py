from rich import print
from fakeredis import aioredis as fake_aioredis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from tensai import utils
from tensai.bot_core import BotManager

import os
import sys
import time
import asyncio
import subprocess
import pkg_resources

print("Checking packages...")

requirements_file = 'requirements.txt'

with open(requirements_file) as f:
    required = f.read().splitlines()

installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

missing_or_outdated = []
for req in required:
    try:
        requirement = pkg_resources.Requirement.parse(req)
        installed_version = installed_packages.get(requirement.key)
        if installed_version is None or installed_version not in requirement:
            missing_or_outdated.append(req)
    except ValueError:
        print(f"⚠️ Error while installing package: {req}")

if missing_or_outdated:
    print(f"Installing missing packages: {', '.join(req for req in missing_or_outdated)}")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_or_outdated])

git_info = asyncio.run(utils.get_git_info())

os.system("cls" if os.name == "nt" else "clear")
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

start_time = time.time()