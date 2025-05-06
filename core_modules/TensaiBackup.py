# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

# description: Backup module of Tensai
# author: @fajox

from aiogram import types

from tensai import bot, db, utils
from tensai.loader import Module
from tensai.update import restart

import time

class TensaiBackup(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "reply_to_backup_file": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Ответье на сообщение с бэкапом БД.</b>",

            "sending_backup": "<i>Отправляю бэкап БД...</i>",
            "restoring_db": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Обновление базы данных...</b>",
            "restarting": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Твой Tensai перезагружается...</b>",
            "backup": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Бэкап базы данных.</b>",
        },

        "en": {
            "reply_to_backup_file": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Reply to a message with DB backup.</b>",

            "sending_backup": "<i>Sending Backup of DB...</i>",
            "restoring_db": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Restoring db...</b>",
            "restarting": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Your Tensai is restarting...</b>",
            "backup": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Backup file of DB.</b>",
        },
    }

    async def _cmd_backupdb(self, message: types.Message):
        """
        - Backup mods
        """
        message = await utils.answer(message, self.strings("sending_backup"))
        await message.answer_document(
            types.FSInputFile("tensai/db/db.json"),
            caption=self.strings("backup")
        )
        await utils.delete_message(message)

    async def _cmd_restoredb(self, message: types.Message):
        """
        - Restore db
        """
        if not message.reply_to_message:
            return await utils.answer(message, self.strings("reply_to_backup_file"))

        file_message = message.reply_to_message
        if not file_message.document:
            return await utils.answer(message, self.strings("reply_to_backup_file"))
        
        message = await utils.answer(message, self.strings("restoring_db"))

        file_id = file_message.document.file_id
        file = await file_message.bot.get_file(file_id)
        await file_message.bot.download_file(file.file_path, destination="tensai/db/db.json")

        message = await utils.answer(message, self.strings("restarting"))
        db.set("tensai.restart.message", {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "business_connection_id": message.business_connection_id,
            "start_time": time.time(),
        })
        await restart()