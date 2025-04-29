from tensai import dp, bot, db, install
from tensai.loader import Loader
from tensai.bot_core import errors

import asyncio
import logging


loader: Loader = Loader()
logger = logging.getLogger(__name__)

async def start_polling() -> None:
    await dp.start_polling(bot, skip_updates=False)

async def run_bot() -> None:
    loader._load_modules()

    print("Starting the bot...")
    logger.info("Starting the bot...")

    await install.install_user()

    await start_polling()
