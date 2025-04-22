# description: simple evaluator module
# author: @vsecoder
# requires: meval

from aiogram import types
from tensai import bot, db, utils
from tensai.loader import Module

from meval import meval  # type: ignore


class Evaluator(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "no_code": "❌ Нет кода для выполнения.",
            "result": "<b>🖥 Код:</b><pre><code class='language-python'>{}</code></pre>\n\n<b>⚙️ Результат:</b><pre><code class='language-python'>{}</code></pre>",
        },
        "en": {
            "no_code": "❌ There is no code to execute.",
            "result": "<b>🖥 Code:</b><pre><code class='language-python'>{}</code></pre>\n\n<b>⚙️ Result:</b><pre><code class='language-python'>{}</code></pre>",
        },
    }

    async def _cmd_eval(self, message: types.Message):
        """
         - evaluate python code
        """
        if message.from_user.id != db.get('tensai.user.telegram_id'):
            return
        
        raw_text = message.text.split(" ", 1)
        if len(raw_text) < 2:
            return await message.edit_text(self.strings('no_code'))

        code = raw_text[1]

        scope = {
            "self": self,
            "db": db,
            "bot": bot,
            "m": message,
            "message": message,
            "r": message.reply_to_message,
            "reply": message.reply_to_message,
        }

        try:
            result = await meval(code, globals(), **scope)
            result_text = utils.escape_html(str(result))
        except Exception as e:
            result_text = utils.escape_html(str(e))

        await message.edit_text(self.strings('result').format(code, result_text))
