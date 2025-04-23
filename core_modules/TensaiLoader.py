# description: module loader
# author: @vsecoder

import os
import aiohttp
from pathlib import Path
from aiogram import types
from aiogram.types import FSInputFile

from tensai.loader import Module
from tensai.main import loader
from tensai import bot


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
        },
        "ru": {
            "missing_reply": "Пожалуйста, ответьте на файл модуля, чтобы загрузить его.",
            "invalid_url": "Неверная ссылка.",
            "download_success": "Модуль загружен и загружен.",
            "load_failed": "Не удалось загрузить модуль.",
            "unload_success": "Модуль выгружен.",
            "unload_failed": "Не удалось выгрузить модуль.",
            "file_not_found": "Файл модуля не найден.",
        }
    }

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
        parts = message.text.split(" ")
        if len(parts) < 2:
            return await message.reply("Module name required.")

        module_name = parts[1]
        path = os.path.join(os.getcwd(), loader.modules_dir, module_name)

        if not os.path.isfile(path):
            return await message.reply(self.strings("file_not_found"))

        await message.reply_document(FSInputFile(path))
