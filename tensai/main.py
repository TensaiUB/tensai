# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

from tensai import dp, bot, db, install
from tensai.loader import Loader
from tensai.bot_core import errors
from tensai.web import start_web

import asyncio
import logging
import sys


loader: Loader = Loader()
logger = logging.getLogger(__name__)

tensai = type(
    "Tensai",
    (),
    {
        "command": loader.command,
        "bot_command": loader.bot_command,
        "inline_command": loader.inline_command,
        "inline": loader.inline,
        "bot_message": loader.bot_message,
        "callback_query": loader.callback_query,
        "business_message": loader.business_message,
        "edited_business_message": loader.edited_business_message,
        "deleted_business_message": loader.deleted_business_message,
    },
)

sys.modules["tensai.decorators"] = tensai

async def start_polling() -> None:
    await start_web()
    await dp.start_polling(bot, skip_updates=False)

async def run_bot() -> None:
    loader._load_modules()

    print("Starting the bot...")
    logger.info("Starting the bot...")

    await install.install_user()

    await start_polling()
