# description: tensai module
# author: @vsecoder, @fajox

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tensai.loader import Module
from tensai import db, utils
from tensai.update import update

import git

SUPPORTED_LANGS = ["ru", "en"]

class TensaiMain(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "tensai-info": """<b>💠 Tensai - быстрый и безопасный юзербот.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">открыть</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Разработчики: @vsecoder & @fajox</b>""",

            "lang": "<b>{flag} Язык установлен: {lang}</b>\n\n{unofficial}",
            "no_support_lang": "<i><tg-emoji emoji-id=5355133243773435190>⚠️</tg-emoji> Данный язык официально не поддерживается.</i>",
            "inccorrect_language": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Некорректный язык.</b>",
            "no_lang": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Язык не выбран.</b>",

            "no_prefix": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Префикс не выбран.</b>",
            "new_prefix": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Префикс обновлён: <code>{new_prefix}</code></b>

<b><tg-emoji emoji-id=5988023995125993550>🛠</tg-emoji> Чтобы изменить обратно:</b>     
<code>{back_to_old_prefix}</code>""",
        },
        "en": {
            "tensai-info": """<b>💠 Tensai - fast and safe userbot.</b>

<b><tg-emoji emoji-id=5346181118884331907>🐈‍⬛</tg-emoji> Github: <a href="https://github.com/TensaiUB/tensai">open</a></b>
            
<tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> <b>Developers: @vsecoder & @fajox</b>""",
            "lang": "<b>{flag} Language saved: {lang}</b>\n\n{unofficial}",
            "no_support_lang": "<i><tg-emoji emoji-id=5355133243773435190>⚠️</tg-emoji> This language is not officially supported.</i>",
            "inccorrect_language": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Incorrect language.</b>",
            "no_lang": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> No language selected.</b>",

            "no_prefix": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> No prefix chosen.</b>",
            "new_prefix": """<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Prefix updated: <code>{new_prefix}</code></b>

<b><tg-emoji emoji-id=5988023995125993550>🛠</tg-emoji> Change it back:</b>     
<code>{back_to_old_prefix}</code>""",
        },
    }

    emoji_flags = {
        "🇪🇳": "<tg-emoji emoji-id=5202196682497859879>🇬🇧</tg-emoji>",
        "🇺🇿": "<tg-emoji emoji-id=5449829434334912605>🇺🇿</tg-emoji>",
        "🇷🇺": "<tg-emoji emoji-id=5449408995691341691>🇷🇺</tg-emoji>",
        "🇺🇦": "<tg-emoji emoji-id=5447309366568953338>🇺🇦</tg-emoji>",
        "🇮🇹": "<tg-emoji emoji-id=5449723275628259037>🇮🇹</tg-emoji>",
        "🇩🇪": "<tg-emoji emoji-id=5409360418520967565>🇩🇪</tg-emoji>",
        "🇪🇸": "<tg-emoji emoji-id=5201957744877248121>🇪🇸</tg-emoji>",
        "🇹🇷": "<tg-emoji emoji-id=5226948110873278599>🇹🇷</tg-emoji>",
        "🇰🇿": "<tg-emoji emoji-id=5228718354658769982>🇰🇿</tg-emoji>",
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

        await message.edit_media(
            media=types.InputMediaAnimation(
                media="https://i.gifer.com/A54z.gif",
                caption=self.strings("tensai-info"),
            ),
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
        lang = utils.get_args(message).lower()
        if not lang:
            return await message.edit_text(self.strings("no_lang"))
        
        flag = utils.country_code_to_emoji(lang)
        if not flag:
            return await message.edit_text(self.strings("inccorrect_language"))
        flag = self.emoji_flags.get(flag, flag)

        db.set("tensai.settings.lang", lang)

        await message.edit_text(self.strings("lang").format(
            flag=flag,
            lang=lang.upper(),
            unofficial=self.strings("no_support_lang") if not lang in SUPPORTED_LANGS else ""
        ))

    async def _cmd_setprefix(self, message: types.Message) -> None:
        """
         <new prefix> - set prefix
        """
        prefix = utils.get_args(message).lower()
        if not prefix:
            return await message.edit_text(self.strings("no_prefix"))
        
        old_prefix = self.get_prefix()

        db.set("tensai.settings.prefix", prefix)

        await message.edit_text(self.strings("new_prefix").format(
            new_prefix=prefix,
            back_to_old_prefix=f"{prefix}setprefix {old_prefix}",
        ))