# description: Security module of Tensai
# author: @fajox

from aiogram import types
from tensai import bot, db, utils
from tensai.loader import Module

class TensaiSecurity(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "no_user_id": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Укажите ID пользователя или ответьте на сообщения пользователя.</b>",
            "invalid_user_id": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Неверный ID пользователя.</b>",

            "already_owner": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Пользователь <code>{user_id}</code> уже является владельцем.</b>",
            "cant_add_yourself": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Вы не можете добавить себя в владельцы.</b>",
            "not_owner": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Пользователь <code>{user_id}</code> не является владельцем.</b>",

            "added_owner": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Пользователь <code>{user_id}</code> добавлен в владельцы.</b>",
            "removed_owner": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> Пользователь <code>{user_id}</code> удален из владельцев.</b>",

            "owners_list": "<b><tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> Текущие владельцы:</b>\n<code>Вы</code>\n{owners}"
        },

        "en": {
            "no_user_id": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Provide User's ID or reply to user's message.</b>",
            "invalid_user_id": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Incorrect User's ID.</b>",

            "already_owner": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> User <code>{user_id}</code> is already an owner.</b>",
            "cant_add_yourself": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> You cannot add yourself as an owner.</b>",
            "not_owner": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> User <code>{user_id}</code> is not an owner.</b>",

            "added_owner": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> User <code>{user_id}</code> has been added as an owner.</b>",
            "removed_owner": "<b><tg-emoji emoji-id=6028565819225542441>✅</tg-emoji> User <code>{user_id}</code> has been removed from owners.</b>",

            "owners_list": "<b><tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji> Current owners:</b>\n<code>You</code>\n{owners}"
        },
    }

    async def _cmd_addowner(self, message: types.Message):
        """
        <user_id or reply to user's mesage> - add owner
        """
        user_id_from_args = utils.get_args(message)
        if not user_id_from_args and not message.reply_to_message:
            return await utils.answer(message, self.strings('no_user_id'))
        
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = user_id_from_args
        
        try:
            user_id = int(user_id)
        except ValueError:
            return await utils.answer(message, self.strings('invalid_user_id'))

        owners = db.get("tensai.security.owners", [])
        if user_id in owners:
            return await utils.answer(message, self.strings('already_owner').format(user_id=user_id))
        if user_id == db.get("tensai.user.telegram_id"):
            return await utils.answer(message, self.strings('cant_add_yourself'))
        
        owners.append(user_id)
        db.set("tensai.security.owners", owners)

        await utils.answer(message, self.strings('added_owner').format(user_id=user_id))

    async def _cmd_removeowner(self, message: types.Message):
        """
        <user_id or reply to user's message> - remove owner
        """
        user_id_from_args = utils.get_args(message)
        if not user_id_from_args and not message.reply_to_message:
            return await utils.answer(message, self.strings('no_user_id'))
        
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = user_id_from_args
        
        try:
            user_id = int(user_id)
        except ValueError:
            return await utils.answer(message, self.strings('invalid_user_id'))

        owners = db.get("tensai.security.owners", [])
        if user_id not in owners:
            return await utils.answer(message, self.strings('not_owner').format(user_id=user_id))
        
        owners.remove(user_id)
        db.set("tensai.security.owners", owners)

        await utils.answer(message, self.strings('removed_owner').format(user_id=user_id))

    async def _cmd_owners(self, message: types.Message):
        """
        - list of owners
        """
        
        owners = db.get("tensai.security.owners", [])        
        owners = "\n".join([f"<code>{owner}</code>" for owner in owners])
        await utils.answer(message, self.strings('owners_list').format(owners=owners))