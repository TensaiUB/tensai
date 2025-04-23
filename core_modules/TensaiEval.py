# description: simple evaluator module
# author: @vsecoder, @fajox
# requires: meval

from aiogram import types
from tensai import bot, db, utils
from tensai.loader import Module

from meval import meval  # type: ignore

import time

class TensaiEval(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "no_code": "<b><tg-emoji emoji-id=5854929766146118183>❌</tg-emoji> Нет кода для выполнения.</b>",
            "executing": "<b><tg-emoji emoji-id=5332600281970517875>🔄</tg-emoji> Выполняю код...</b>",
            "result": """<b><tg-emoji emoji-id=5431376038628171216>💻</tg-emoji> Код:</b>
<pre><code class='language-python'>{code}</code></pre>

<b><tg-emoji emoji-id=5472164874886846699>✨</tg-emoji> Результат:</b>
<pre><code class='language-python'>{result}</code></pre>

<b>Выполнилось за <b>{seconds}</b> секунд</b>""",
        },

        "en": {
            "no_code": "<b><tg-emoji emoji-id=5854929766146118183>❌</tg-emoji> There is no code to execute.</b>",
            "executing": "<b><tg-emoji emoji-id=5332600281970517875>🔄</tg-emoji> Executing code...</b>",
            "result": """<b><tg-emoji emoji-id=5431376038628171216>💻</tg-emoji> Code:</b>
<pre><code class='language-python'>{code}</code></pre>

<b><tg-emoji emoji-id=5472164874886846699>✨</tg-emoji> Result:</b>
<pre><code class='language-python'>{result}</code></pre>

<b>Completed in <b>{seconds}</b> seconds</b>""",
        },
    }

    async def _cmd_e(self, message: types.Message):
        """
         - evaluate python code
        """
        
        code = utils.get_args(message)
        if not code:
            return await message.edit_text(self.strings('no_code'))
        
        await message.edit_text(self.strings('executing'))

        scope = {
            "self": self,
            "db": db,
            "bot": bot,
            "m": message,
            "message": message,
            "r": message.reply_to_message,
            "reply": message.reply_to_message,
        }

        start_time = time.perf_counter()
        try:
            result = await meval(code, globals(), **scope)
            result_text = utils.escape_html(str(result))
        except Exception as e:
            result_text = utils.escape_html(str(e))
        stop_time = time.perf_counter()

        await message.edit_text(self.strings('result').format(
            code=code,
            result=result_text,
            seconds=round(stop_time - start_time, 2),
        ))