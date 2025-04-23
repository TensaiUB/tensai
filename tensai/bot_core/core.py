from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tensai import db

from rich import print

class BotManager:
    def __init__(self) -> None:
        self.bot: types.Bot | None = None
        self.dp: Dispatcher | None = None

    def _install_bot(self) -> str:
        """Install the bot."""
    
        print("\n[italic cornflower_blue]Installing Tensai bot...[/italic cornflower_blue]")

        while True:
            token: str = input("Enter your bot token from @BotFather (make sure business mode is on): ")

            try:
                Bot(
                    token=token,
                        default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    )
                )
            except Exception as e:
                print(f"Invalid token. Please try again. Error: {e}")
                continue

            break

        return token

    def load(self) -> tuple[Bot, Dispatcher]:
        """Bot loading."""

        token: str | None = db.get('tensai.bot.token', None)

        if not token:
            token: str = self._install_bot()
            db.set('tensai.bot.token', token)
            token: str = db.get('tensai.bot.token')

        self.bot: Bot = Bot(
            token=token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            )
        )
        self.dp: Dispatcher = Dispatcher()

        print("Bot loaded successfully.")

        return self.bot, self.dp