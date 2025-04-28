from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tensai import db, web

from rich import print

import asyncio
import time


class BotManager:
    def __init__(self) -> None:
        self.bot: types.Bot | None = None
        self.dp: Dispatcher | None = None
        self.start_time: float = time.time()

    def _install_bot(self) -> str:
        """Install the bot."""

        print("\n[italic cornflower_blue]Installing Tensai bot...[/italic cornflower_blue]")

        while True:
            token: str = input("Enter your bot token from @BotFather (make sure business mode is on): ")

            if not self._validate_token(token):
                print(f"Invalid token. Please try again.")
                continue

            break

        return token

    def load(self) -> tuple[Bot, Dispatcher]:
        """Bot loading."""

        token: str | None = db.get('tensai.bot.token', "")

        if not token or not self._validate_token(token):
            token = self._get_token_via_installer()
            db.set('tensai.bot.token', token)

        self.bot: Bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp: Dispatcher = Dispatcher()

        print("Bot loaded successfully.")

        return self.bot, self.dp

    def _validate_token(self, token: str) -> bool:
        try:
            Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            return True
        except Exception:
            return False

    def _get_token_via_installer(self) -> str:
        if not db.get("tensai.settings.web.use_web"):
            return self._install_bot()
        return asyncio.run(web.start_webinstaller())
