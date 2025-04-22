# description: tensai module
# author: @vsecoder

from aiogram import types
from tensai.loader import Module
from tensai import loader, db


class Tensai(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "info": (
                "Tensai - так называют робота, который знает всё и умеет всё.\n"
                "Он использует Telegram Bussiness API, поэтому не нарушает никаких правил.\n"
                "Но работает он только в ЛС, так что используется для бизнеса.\n"
            ),
            "help_cmd": " - {}{} {}\n",
            "help_module": "{}:\n",
        },
        "en": {
            "info": (
                "Tensai - so-called robot who knows everything and can do everything.\n"
                "He uses Telegram Bussiness API, so he doesn't break any rules.\n"
                "But he works only in private chat, so he is used for business.\n"
            )
        },
    }

    async def _cmd_tensai(self, message: types.Message) -> None:
        """
         - get info
        """
        if message.from_user.id != db.get('tensai.user.telegram_id'):
            return

        await message.edit_text(self.strings("info"))
