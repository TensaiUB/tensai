# description: tensai translate module
# author: @fajox
# requires: aiohttp

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tensai.loader import Module
from tensai import bot, db, utils
from tensai.decorators import command
from tensai.update import restart

import ssl
import aiohttp

SUPPORTED_LANGS = ["ru", "en"]

class TensaiTranslator(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "no_support_lang": "<i><tg-emoji emoji-id=5355133243773435190>⚠️</tg-emoji> Данный язык официально не поддерживается.</i>",
            "inccorrect_language": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Некорректный язык.</b>",
            "no_lang": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Язык не выбран.</b>",
            "lang": "<b>{flag} Язык установлен: {lang}</b>\n\n{unofficial}",
            "choose_language": "<b><tg-emoji emoji-id=5785209342986817408>🌎</tg-emoji> Выберите свой язык:</b>",

            "no_args_translate": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Используйте <code>{}tr [язык] [текст]</code></b>"
        },
        "en": {
            "no_support_lang": "<i><tg-emoji emoji-id=5355133243773435190>⚠️</tg-emoji> This language is not officially supported.</i>",
            "inccorrect_language": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Incorrect language.</b>",
            "no_lang": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> No language selected.</b>",
            "lang": "<b>{flag} Язык установлен: {lang}</b>\n\n{unofficial}",
            "choose_language": "<b><tg-emoji emoji-id=5785209342986817408>🌎</tg-emoji> Choose your language:</b>",

            "no_args_translate": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Use <code>{}tr [to_lang] [text]</code></b>"
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

    async def on_load(self):
        self.ssl = ssl.create_default_context()
        self.ssl.check_hostname = False
        self.ssl.verify_mode = ssl.CERT_NONE

    async def _cmd_setlang(self, message: types.Message) -> None:
        """
         <lang> - set language
        """
        lang = utils.get_args(message).lower()
        if not lang:
            keyboard = InlineKeyboardBuilder()

            for i in range(0, len(SUPPORTED_LANGS), 3):
                row = [
                    types.InlineKeyboardButton(text=f"{utils.country_code_to_emoji(lang)} {lang.upper()}", callback_data=f"tensai_settings:setlang:{lang}")
                    for lang in SUPPORTED_LANGS[i:i+3]
                ]
                keyboard.row(*row)

            return await utils.answer(
                message=message,
                text=self.strings("choose_language"),
                reply_markup=keyboard.as_markup()
            )
        
        flag = utils.country_code_to_emoji(lang)
        if not flag:
            return await utils.answer(message, self.strings("inccorrect_language"))
        flag = self.emoji_flags.get(flag, flag)

        db.set("tensai.settings.lang", lang)

        await utils.answer(message, self.strings("lang").format(
            flag=flag,
            lang=lang.upper(),
            unofficial=self.strings("no_support_lang") if lang not in SUPPORTED_LANGS else ""
        ))

    async def _cbq_setlang(self, callback: types.CallbackQuery):
        """
         - set lang by buttons
        """
        if not callback.data.startswith("tensai_settings:setlang:"):
            return
        if callback.from_user.id != db.get("tensai.user.telegram_id", 0):
            return
        
        lang = callback.data.split(":")[2]
        
        db.set("tensai.settings.lang", lang)

        flag = utils.country_code_to_emoji(lang)
        flag = self.emoji_flags.get(flag, flag)

        return await callback.message.edit_text(
            text=self.strings("lang").format(
                flag=flag,
                lang=lang.upper(),
                unofficial=self.strings("no_support_lang") if lang not in SUPPORTED_LANGS else ""
            )
        )
    
    @command(
        aliases=["translate", "tr"],
        description={
            "en": "<to lang> <text> - translate text",
            "ru": "<язык> <текст> - перевести текст"
        }
    )
    async def _cmd_tr(self, message: types.Message) -> None:
        """
         <to lang> <text> - translate text
        """
        try:
            to_lang, text = utils.get_args(message).split(" ")
        except:
            if message.reply_to_message:
                to_lang = utils.get_args(message)
                text = message.reply_to_message.text
            else:
                return await utils.answer(message, self.strings("no_args_translate").format(
                    self.get_prefix()
                ))
        
        url = f"https://lingva.ml/api/v1/auto/{to_lang}/{text}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=self.ssl) as response:
                data = await response.json()
                result = data['translation']

        return await utils.answer(message, result)