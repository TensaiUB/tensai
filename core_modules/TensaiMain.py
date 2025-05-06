# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

# description: tensai module
# author: @vsecoder, @fajox

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tensai.loader import Module
from tensai.decorators import callback_query
from tensai import bot, db, utils
from tensai.update import restart

import git
import time
import asyncio

class TensaiMain(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "tensai-info": """<b>💠 Tensai - быстрый и безопасный юзербот.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">открыть</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Разработчики: @vsecoder & @fajox</b>""",

            "no_prefix": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Префикс не выбран.</b>",
            "new_prefix": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Префикс обновлён: <code>{new_prefix}</code></b>

<b><tg-emoji emoji-id=5988023995125993550>🛠</tg-emoji> Чтобы изменить обратно:</b>     
<code>{back_to_old_prefix}</code>""",

            "restarting": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Твой Tensai перезагружается...</b>",
            "restarted": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Tensai успешно перезагрузился!</b>
<i>Перезагрузка заняла {sec} секунд</i>""",

            "checking_update": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Проверка обновлений...</b>",
            "updating": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Обновление...</b>",
            "no_update": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Установлена последняя версия!</b>",

            "bot_update_notification": """<b>🔄 Вышло обновление! <a href="{local_commit_link}">{local_commit}</a> → <a href="{remote_commit_link}">{remote_commit}</a>
            
🌳 Ветка: <code>{branch}</code></b>""",

            "source-code": "<tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> <b>Tensai полностью открыт. Исходный код можно найти на Github.</b>"
        },
        "en": {
            "tensai-info": """<b>💠 Tensai - fast and safe userbot.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">open</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Developers: @vsecoder & @fajox</b>""",

            "no_prefix": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> No prefix chosen.</b>",
            "new_prefix": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Prefix updated: <code>{new_prefix}</code></b>

<b><tg-emoji emoji-id=5988023995125993550>🛠</tg-emoji> Change it back:</b>     
<code>{back_to_old_prefix}</code>""",

            "restarting": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Your Tensai is restarting...</b>",
            "restarted": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Tensai restarted successfully!</b>
<i>Restart took {sec} seconds</i>""",

            "checking_update": "<b><tg-emoji emoji-id=5325731315004218660>🔄</tg-emoji> Checking for updates...</b>",
            "updating": "<b><tg-emoji emoji-id=5328274090262275771>🔄</tg-emoji> Updating...</b>",
            "no_update": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Latest version installed!</b>",

            "bot_update_notification": """<b>🔄 New update! <a href="{local_commit_link}">{local_commit}</a> → <a href="{remote_commit_link}">{remote_commit}</a>
            
🌳 Branch: <code>{branch}</code></b>""",

            "source-code": "<tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> <b>Tensai is full open-souce. You can find it on Github.</b>"
        },
    }

    async def on_load(self) -> None:
        asyncio.create_task(self.update_checker())

        restart_message = db.get("tensai.restart.message", None)
        if not restart_message:
            return
        db.set("tensai.restart.message", None)
        db.set("tensai.restart.do_not_restart", None)
        
        await bot.edit_message_text(
            chat_id=restart_message["chat_id"],
            message_id=restart_message["message_id"],
            business_connection_id=restart_message["business_connection_id"],
            text=self.strings("restarted").format(
                sec=int(time.time() - restart_message["start_time"]),
            )
        )

    async def _cmd_tensai(self, message: types.Message) -> None:
        """
         - get info
        """
        keyboard = InlineKeyboardBuilder()

        keyboard.row(
            types.InlineKeyboardButton(
                text="Github",
                url="https://github.com/TensaiUB/tensai",
            )
        )

        await utils.answer_media(
            message=message,
            media=types.InputMediaAnimation(
                media="https://i.gifer.com/A54z.gif",
                caption=self.strings("tensai-info"),
            ),
            reply_markup=keyboard.as_markup()
        )

    async def _cmd_source(self, message: types.Message) -> None:
        """
         - get source code
        """
        keyboard = InlineKeyboardBuilder()

        keyboard.row(
            types.InlineKeyboardButton(
                text="Dev #1",
                url="https://t.me/fajox",
            ),
            types.InlineKeyboardButton(
                text="Dev #2",
                url="https://t.me/vsecoder",
            )
        )

        keyboard.row(
            types.InlineKeyboardButton(
                text="Github",
                url="https://github.com/TensaiUB/tensai",
            )
        )

        keyboard.row(
            types.InlineKeyboardButton(
                text="Channel",
                url="https://t.me/tensai_ub",
            ),
            types.InlineKeyboardButton(
                text="Chat",
                url="https://t.me/tensai_chat",
            )
        )

        await utils.answer(
            message=message,
            text=self.strings("source-code"),
            reply_markup=keyboard.as_markup()
        )

    async def _cmd_update(self, message: types.Message) -> None:
        """
         - update tensai
        """
        message = await utils.answer(message, self.strings("checking_update"))

        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin

        origin.fetch()

        local_commit = repo.head.commit.hexsha
        remote_commit = repo.refs[f"origin/{repo.active_branch.name}"].commit.hexsha

        if local_commit != remote_commit:
            await utils.answer(message, self.strings("updating"))
            origin.pull()
            await self._cmd_restart(message)
        else:
            await utils.answer(message, self.strings("no_update"))

    async def _cmd_setprefix(self, message: types.Message) -> None:
        """
         <new prefix> - set prefix
        """
        prefix = utils.get_args(message).lower()
        if not prefix:
            return await utils.answer(message, self.strings("no_prefix"))
        
        old_prefix = self.get_prefix()

        db.set("tensai.settings.prefix", prefix)

        await utils.answer(message, self.strings("new_prefix").format(
            new_prefix=prefix,
            back_to_old_prefix=f"{prefix}setprefix {old_prefix}",
        ))

    async def _cmd_restart(self, message: types.Message) -> None:
        """
         - restart tensai
        """
        message = await utils.answer(message, self.strings("restarting"))
        db.set("tensai.restart.message", {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "business_connection_id": message.business_connection_id,
            "start_time": time.time(),
        })
        await restart()

    async def _botcmd_start(self, message: types.Message) -> None:
        """
         - bot's start command
        """
        
        keyboard = InlineKeyboardBuilder()

        keyboard.row(
            types.InlineKeyboardButton(
                text="Github",
                url="https://github.com/TensaiUB/tensai",
            )
        )

        await message.answer_animation(
            animation="https://i.gifer.com/A54z.gif",
            caption=self.strings("tensai-info"),
            reply_markup=keyboard.as_markup()
        )

    @callback_query(
        data="tensai_update",
        description={
            "en": "- update tensai",
            "ru": "- обновить tensai"
        }
    )
    async def button_update(self, callback: types.CallbackQuery) -> None:
        
        await callback.message.delete()
        message = await callback.message.answer(self.strings("updating"))

        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin
        origin.pull()

        message = await message.edit_text(self.strings("restarting"))
        db.set("tensai.restart.message", {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "business_connection_id": None,
            "start_time": time.time(),
        })
        await restart()

    async def update_checker(self) -> None:

        keyboard = InlineKeyboardBuilder()

        keyboard.row(
            types.InlineKeyboardButton(
                text="🔄 Update",
                callback_data="tensai_update",
            )
        )

        while True:
            repo = git.Repo(search_parent_directories=True)
            origin = repo.remotes.origin

            origin.fetch()

            local_commit = repo.head.commit.hexsha
            remote_commit = repo.refs[f"origin/{repo.active_branch.name}"].commit.hexsha

            if local_commit == remote_commit:
                break

            owner = db.get("tensai.user.telegram_id")

            await bot.send_animation(
                chat_id=owner,
                animation="https://i.gifer.com/3WMZ.gif",
                caption=self.strings("bot_update_notification").format(
                    local_commit=local_commit[:7],
                    remote_commit=remote_commit[:7],
                    local_commit_link=f"https://github.com/TensaiUB/tensai/commit/{local_commit}",
                    remote_commit_link=f"https://github.com/TensaiUB/tensai/commit/{remote_commit}",
                    branch=repo.active_branch.name,
                ),
                reply_markup=keyboard.as_markup()
            )

            await asyncio.sleep(300)