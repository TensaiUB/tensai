# description: tensai module
# author: @vsecoder, @fajox

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tensai.loader import Module
from tensai import db, utils
from tensai.update import update

import git

class TensaiMain(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "tensai-info": """<b>💠 Tensai - быстрый и безопасный юзербот.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">открыть</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Разработчики: @fajox & @vsecoder</b>""",
            "lang": "<b>Выбранный язык: {}</b>",
            "no_lang": "<b>Язык не выбран.</b>",
        },
        "en": {
            "tensai-info": """<b>💠 Tensai - fast and safe userbot.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">open</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Developers: @fajox & @vsecoder</b>""",
            "lang": "<b>Selected language: {}</b>",
            "no_lang": "<b>No language selected.</b>",
        },
    }

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

        await message.answer_animation(
            animation="https://i.gifer.com/A54z.gif",
            caption=self.strings("tensai-info"),
            reply_markup=keyboard.as_markup()
        )

    async def _cmd_update(self, message: types.Message) -> None:
        """
         - update tensai
        """
        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin

        origin.fetch()

        local_commit = repo.head.commit.hexsha
        remote_commit = repo.refs[f"origin/{repo.active_branch.name}"].commit.hexsha

        if local_commit != remote_commit:
            await message.edit_text("New update available, updating...")
            await update(origin)
        else:
            await message.edit_text("No new update available.")

    async def _cmd_setlang(self, message: types.Message) -> None:
        """
         <lang> - set language
        """
        lang = utils.get_args(message)
        if not lang:
            return await message.edit_text(self.strings("no_lang"))

        db.set("tensai.settings.lang", lang)

        await message.edit_text(self.strings("lang").format(lang))
