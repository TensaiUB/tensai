# description: simple ping module
# author: @vsecoder, @fajox

import time
from aiogram import types
from tensai import db
from tensai.loader import Module

class TensaiTester(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "ping": "<b><tg-emoji emoji-id=5931472654660800739>🏓</tg-emoji> Понг! Пинг <code>{ms}</code> ms.</b>",
        },
        "en": {
            "ping": "<b><tg-emoji emoji-id=5931472654660800739>🏓</tg-emoji> Pong! Ping <code>{ms}</code> ms.</b>",
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
        await message.edit_text(self.strings('ping').format(ms=ping_ms))