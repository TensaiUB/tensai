# description: simple ping module
# author: @vsecoder

import time
from aiogram import types
from tensai import db
from tensai.loader import Module


class Ping(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "ping": "🏓 Понг! <b>{}</b>",
        },
        "en": {
            "ping": "🏓 Pong! <b>{}</b>",
        },
    }

    async def _cmd_ping(self, message: types.Message) -> None:
        """
         - get ping
        """
        if message.from_user.id != db.get('tensai.user.telegram_id'):
            return

        start = time.monotonic()
        await message.edit_text("🏓")
        end = time.monotonic()

        ping_ms = int((end - start) * 1000)
        await message.edit_text(self.strings('ping').format(ping_ms))
