# description: selflog module
# author: @vsecoder

import os
import asyncio
from aiogram import types
from aiogram.types import BusinessMessagesDeleted, FSInputFile
from tensai.loader import Module
from tensai import bot, redis, db


class TensaiSelflog(Module):
    async def _cmd_setchat(self, message: types.Message):
        """
        <chat_id> - enter chat id for selflog
        """
        admin_id = db.get("tensai.user.telegram_id")
        if message.from_user.id != admin_id:
            return

        chat_id = message.text.split()[1]
        if not chat_id:
            return

        db.set("tensai.selflog.chat_id", chat_id)
        await message.reply("<b>✅ Selflog chat has been changed!</b>")

    async def _bismsg_selflog(self, message: types.Message):
        await self.set_message(message)

        admin_id = db.get("tensai.user.telegram_id")
        log_chat_id = db.get("tensai.selflog.chat_id")

        if not message.reply_to_message:
            return

        if (
            message.from_user.id != admin_id
            or message.reply_to_message.from_user.id == admin_id
        ):
            return

        model_dump = await redis.get(f"{message.chat.id}:{message.reply_to_message.message_id}")
        if model_dump:
            return

        user = db.get(f"tensai.selflog.users.{message.reply_to_message.from_user.id}")
        if not user:
            return

        await bot.send_message(
            chat_id=log_chat_id,
            text="<b>🔥 Self destructed message:</b>",
            message_thread_id=user["topic_id"],
        )

        reply = message.reply_to_message
        file_id, file_type = None, None

        if reply.photo:
            file_id, file_type = reply.photo[-1].file_id, "jpg"
        elif reply.video:
            file_id, file_type = reply.video.file_id, "mp4"
        elif reply.voice:
            file_id, file_type = reply.voice.file_id, "ogg"
        elif reply.video_note:
            file_id, file_type = reply.video_note.file_id, "mp4"

        if file_id and file_type:
            await self.send_media(bot, log_chat_id, user, file_type, file_id)

    async def _bisedit_selflog(self, message: types.Message):
        model_dump = await redis.get(f"{message.chat.id}:{message.message_id}")
        if not model_dump:
            return

        original_message = types.Message.model_validate_json(model_dump)
        if not original_message.from_user:
            return

        user = db.get(f"tensai.selflog.users.{original_message.from_user.id}")
        if not user:
            return

        log_chat_id = db.get("tensai.selflog.chat_id")

        await bot.send_message(
            chat_id=log_chat_id,
            message_thread_id=user["topic_id"],
            text="<b>✏️ Edit message, old message:</b>",
        )

        await original_message.send_copy(
            chat_id=log_chat_id,
            message_thread_id=user["topic_id"],
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(
                        text="Открыть",
                        url=f"tg://openmessage?user_id={original_message.from_user.id}&message_id={original_message.message_id}"
                    )
                ]]
            )
        ).as_(bot)

    async def _bisdel_selflog(self, business_messages: BusinessMessagesDeleted):
        pipe = redis.pipeline()
        for message_id in business_messages.message_ids:
            pipe.get(f"{business_messages.chat.id}:{message_id}")
        messages_data = await pipe.execute()

        log_chat_id = db.get("tensai.selflog.chat_id")
        keys_to_delete = []

        for message_id, model_dump in zip(business_messages.message_ids, messages_data):
            if not model_dump:
                continue

            original_message = types.Message.model_validate_json(model_dump)
            if not original_message.from_user:
                continue

            user = db.get(f"tensai.selflog.users.{original_message.from_user.id}")
            if not user:
                continue

            await bot.send_message(
                chat_id=log_chat_id,
                message_thread_id=user["topic_id"],
                text="<b>🗑 Deleted message:</b>",
            )

            await original_message.send_copy(
                chat_id=log_chat_id,
                message_thread_id=user["topic_id"],
            ).as_(bot)

            await asyncio.sleep(1.2)
            keys_to_delete.append(f"{business_messages.chat.id}:{message_id}")

        if keys_to_delete:
            await redis.delete(*keys_to_delete)

    async def set_message(self, message: types.Message):
        admin_id = db.get("tensai.user.telegram_id")
        log_chat_id = db.get("tensai.selflog.chat_id")

        if message.from_user.id == admin_id:
            return

        user = db.get(f"tensai.selflog.users.{message.from_user.id}")
        if not user:
            topic = await bot.create_forum_topic(chat_id=log_chat_id, name=message.from_user.full_name)

            await bot.send_message(
                chat_id=log_chat_id,
                text=f"<b>{message.from_user.full_name}</b> (@{message.from_user.username})",
                message_thread_id=topic.message_thread_id,
            )

            db.set(f"tensai.selflog.users.{message.from_user.id}", {
                "id": message.from_user.id,
                "topic_id": topic.message_thread_id
            })

        await redis.set(
            f"{message.chat.id}:{message.message_id}",
            message.model_dump_json(),
            ex=60 * 60 * 24 * 21
        )

    async def send_media(self, bot, chat_id, user, media_type, file_id):
        file_path = f"{file_id}.{media_type}"
        await bot.download(file_id, destination=file_path)

        media = FSInputFile(file_path)
        if media_type == "jpg":
            await bot.send_photo(chat_id=chat_id, message_thread_id=user["topic_id"], photo=media)
        elif media_type == "mp4":
            if "video_note" in file_id:
                await bot.send_video_note(chat_id=chat_id, message_thread_id=user["topic_id"], video_note=media)
            else:
                await bot.send_video(chat_id=chat_id, message_thread_id=user["topic_id"], video=media)
        elif media_type == "ogg":
            await bot.send_voice(chat_id=chat_id, message_thread_id=user["topic_id"], voice=media)

        await asyncio.sleep(1.2)
        os.remove(file_path)
