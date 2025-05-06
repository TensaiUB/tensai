# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

# description: module loader
# author: @vsecoder, @fajox

import os
import aiohttp
from pathlib import Path
from aiogram import types
from fuzzywuzzy import fuzz
from aiogram.types import FSInputFile

from tensai.loader import Module
from tensai.main import loader
from tensai import bot, utils

class TensaiLoader(Module):
    strings = {
        "en": {
            "missing_reply": "Please reply to a module file to load it.",
            "invalid_url": "Invalid URL.",
            "download_success": "Module downloaded and loaded.",
            "load_failed": "Failed to load module.",
            "unload_success": "Module unloaded.",
            "unload_failed": "Failed to unload module.",
            "file_not_found": "Module file not found.",

            "no_module_name": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Требуется имя модуля.</b>",
            "module_not_found": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Модуль не найден.</b>",
            "searching_module": "<b><tg-emoji emoji-id=5366045973988522066>✨</tg-emoji> Ищу модуль...</b>",
            "ml_module_info": """<b><tg-emoji emoji-id=5256113064821926998>📁</tg-emoji> Модуль <code>{module_name}</code>.
            
<tg-emoji emoji-id=5883973610606956186>💬</tg-emoji> <code>.lm</code> в ответ для установки</b>""",
        },
        "ru": {
            "missing_reply": "Пожалуйста, ответьте на файл модуля, чтобы загрузить его.",
            "invalid_url": "Неверная ссылка.",
            "download_success": "Модуль загружен и загружен.",
            "load_failed": "Не удалось загрузить модуль.",
            "unload_success": "Модуль выгружен.",
            "unload_failed": "Не удалось выгрузить модуль.",
            "file_not_found": "Файл модуля не найден.",

            "no_module_name": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Module name required.</b>",
            "module_not_found": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Module not found.</b>",
            "searching_module": "<b><tg-emoji emoji-id=5366045973988522066>✨</tg-emoji> Searching module...</b>",
            "ml_module_info": """<b><tg-emoji emoji-id=5256113064821926998>📁</tg-emoji> Module <code>{module_name}</code>.
            
<tg-emoji emoji-id=5883973610606956186>💬</tg-emoji> <code>.lm</code> in reply for install</b>""",
        }
    }

    async def on_load(self) -> None:
        self.modules_dirs = [
            loader.modules_dir,
            loader.core_modules_dir
        ]

    async def _request(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def _cmd_lm(self, message: types.Message) -> None:
        """
         - load module from a replied file
        """
        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply(self.strings("missing_reply"))

        file_name = message.reply_to_message.document.file_name
        path = os.path.join(os.getcwd(), loader.modules_dir, file_name)
        name = file_name.replace(".py", "")

        if name in loader.modules:
            await message.reply("Module already loaded, deleting...")
            loader.unload_module(name)

        try:
            await bot.download(message.reply_to_message.document.file_id, destination=path)
            loader.load_module(Path(path))
            await message.reply(self.strings("download_success"))
        except Exception:
            await message.reply(self.strings("load_failed"))

    async def _cmd_dlm(self, message: types.Message) -> None:
        """
         <url> - load module from URL
        """
        parts = message.text.split(" ")
        if len(parts) < 2 or not parts[1].startswith("http"):
            return await message.reply(self.strings("invalid_url"))

        url = parts[1]
        name = url.split("/")[-1]
        path = os.path.join(os.getcwd(), loader.modules_dir, name)

        if name in loader.modules:
            await message.reply("Module already loaded, deleting...")
            loader.unload_module(name)

        try:
            code = await self._request(url)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            loader.load_module(Path(path))
            await message.reply(self.strings("download_success"))
        except Exception:
            await message.reply(self.strings("load_failed"))

    async def _cmd_ulm(self, message: types.Message) -> None:
        """
         <name> - unload module
        """
        parts = message.text.split(" ")
        if len(parts) < 2:
            return await message.reply("Module name required.")

        module_name = parts[1]
        try:
            loader.unload_module(module_name)
            await message.reply(self.strings("unload_success"))
        except Exception:
            await message.reply(self.strings("unload_failed"))

    async def _cmd_ml(self, message: types.Message) -> None:
        """
        <name> - send module as file
        """
        module_name = utils.get_args(message)
        if not module_name:
            return await utils.answer(message, self.strings("no_module_name"))
        
        m = await utils.answer(message, self.strings("searching_module"))

        best_match_path = None
        best_match_score = 0

        for modules_dir in self.modules_dirs:
            for root, dirs, files in os.walk(modules_dir):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    filename_no_ext = os.path.splitext(file)[0]
                    
                    if filename_no_ext.startswith("_"):
                        continue

                    score = fuzz.partial_ratio(module_name.lower(), filename_no_ext.lower())

                    if score > best_match_score:
                        best_match_score = score
                        best_match_path = os.path.join(root, file)

        if best_match_score < 80:
            return await utils.answer(message, self.strings("module_not_found"))
        
        module_name = os.path.basename(best_match_path).replace(".py", "")

        await message.reply_document(
            FSInputFile(best_match_path),
            caption=self.strings("ml_module_info").format(module_name=module_name),
        )