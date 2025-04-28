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

from rich import print
from fakeredis import aioredis as fake_aioredis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from tensai import db, utils
from tensai.bot_core import BotManager

import os
import sys
import time
import asyncio
import argparse

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

if '--use-web' in sys.argv:
    web = True
elif '--no-web' in sys.argv:
    web = False
else:
    if not db.get("tensai.settings.web"):
        web_input = input("\nDo you want to use web as default? (y/n): ").strip().lower()
        web = web_input == "y"
    else:
        web = db.get("tensai.settings.web.use_web")

port = db.get("tensai.settings.web.port", 8080)

if web:
    parser = argparse.ArgumentParser(description="Get args")
    parser.add_argument('--port', type=str, help='Port', required=False)
    args, unknown = parser.parse_known_args()

    if args.port:
        port = args.port
    else:
        if not db.get("tensai.settings.web"):
            port_input = input("What port do you want to use? (Press enter to use default 8080): ").strip()
            if port_input:
                port = int(port_input)

db.set("tensai.settings.web", {
    "use_web": web,
    "port": port
})

manager = BotManager()
bot, dp = manager.load()

start_time = time.time()