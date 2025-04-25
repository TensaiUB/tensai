from aiogram import types

from tensai import dp, db, bot, utils

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
        await utils.answer(
            update.business_message,
            text=formatted_traceback
        )
    except Exception:
        try:
            await utils.answer(
                update.message.edit_text,
                text=formatted_traceback
            )
        except:
            pass
        await bot.send_message(
            chat_id=db.get("tensai.user.telegram_id"), text=formatted_traceback
        )