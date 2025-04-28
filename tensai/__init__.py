from .dependencies import check_dependencies

from rich import print
from tensai import db
from .utils import get_git_info
from .settings import get_redis, get_web_settings
from .bot_core.core import BotManager

import os
import sys
import time
import asyncio


git_info = asyncio.run(get_git_info())
os.system("cls" if os.name == "nt" else "clear")
print(
        f"""[sky_blue1] _____                    _ 
|_   _|__ _ __  ___  __ _(_)
  | |/ _ \ '_ \/ __|/ _` | |
  | |  __/ | | \__ \ (_| | |
  |_|\___|_| |_|___/\__,_|_|

Commit: #{git_info['last_commit_short']}
Github: https://github.com/TensaiUB/tensai[/sky_blue1]
"""
)
manager = BotManager()
bot, dp = manager.load()
start_time = time.time()

redis = asyncio.run(get_redis())
web, port = get_web_settings(db, sys.argv)
