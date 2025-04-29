# description: simple ping module
# author: @vsecoder, @fajox

from aiogram import types

from tensai import start_time, utils
from tensai.loader import Module
from tensai.decorators import command

import time

class TensaiTester(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "ping": "<b><tg-emoji emoji-id=5931472654660800739>🏓</tg-emoji> Понг! Пинг <code>{ms}</code> ms.</b>",
            "uptime": "<b><tg-emoji emoji-id=5431449001532594346>⚡️</tg-emoji> Текущий аптайм: <code>{uptime}</code></b>",
        },
        "en": {
            "ping": "<b><tg-emoji emoji-id=5931472654660800739>🏓</tg-emoji> Pong! Ping <code>{ms}</code> ms.</b>",
            "uptime": "<b><tg-emoji emoji-id=5431449001532594346>⚡️</tg-emoji> Current uptime: <code>{uptime}</code></b>",
        },
    }

    @command(
        aliases=["ping", "p"], description={"ru": " - получить пинг", "en": " - get ping"}
    )
    async def _cmd_ping(self, message: types.Message) -> None:
        start = time.monotonic()
        await utils.answer(message, "🏓")
        end = time.monotonic()

        ping_ms = int((end - start) * 1000)
        await utils.answer(message, self.strings('ping').format(ms=ping_ms))

    @command(aliases=["uptime"])
    async def _cmd_uptime(self, message: types.Message) -> None:
        """
         - get uptime
        """

        uptime = time.time() - start_time
        uptime = time.strftime("%H:%M:%S", time.gmtime(uptime))

        await utils.answer(message, self.strings('uptime').format(uptime=uptime))

    @command(
        aliases=["logs"]
    )
    async def _cmd_logs(self, message: types.Message) -> None:
        """
         - get logs
        """
        await utils.answer(message, "<b>Logs:</b>")
        await message.answer_document(types.FSInputFile("tensai.log"))
