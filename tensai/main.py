from tensai import dp, bot, db, install
from tensai.loader import Loader
from tensai.update import auto_updater

import asyncio

loader: Loader = Loader()

async def start_polling() -> None:
    await dp.start_polling(bot, skip_updates=False)

async def run_bot() -> None:
    loader._load_modules()

    print("Starting the bot...")

    user_data: str | None = db.get('tensai.user', None)
    if not user_data:
        await install.install_user()

    await start_polling()

    asyncio.create_task(auto_updater())
