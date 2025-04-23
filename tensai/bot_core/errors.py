from aiogram import types

from tensai import dp, db

import html
import traceback

@dp.error()
async def error_handler(event: types.ErrorEvent):
    bot_token = db.get("tensai.bot.token")

    update = event.update
    exception = event.exception

    print(exception)

    last_frame = traceback.extract_tb(exception.__traceback__)[-1]

    formatted_traceback = f"""<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> An error occurred:</b>
<blockquote><b>File:</b> <code>{html.escape(last_frame.filename)}</code>
<b>Line:</b> <code>{last_frame.lineno}</code>
<b>Name:</b> <code>{html.escape(exception.__class__.__name__)}</code>
<b>Function:</b> <code>{html.escape(last_frame.name)}</code>
<b>Message:</b> <code>{html.escape(str(exception))}</code>
<b>Code:</b> <code>{html.escape(last_frame.line)}</code></blockquote>""".replace(
        bot_token, "[hidden]"
    )

    try:
        await update.business_message.edit_text(
            text=formatted_traceback
        )
    except Exception:
        await update.message.edit_text(
            text=formatted_traceback
        )
