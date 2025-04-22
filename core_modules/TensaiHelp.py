# description: help module
# author: @vsecoder, @fajox

from aiogram import types
from tensai.loader import Module
from tensai import db
from tensai.main import loader
from tensai.utils import escape_html

class TensaiHelp(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "help_header": "<tg-emoji emoji-id=5883973610606956186>🗂</tg-emoji> <b>Доступные модули и команды:</b>\n\n",
            "no_doc": "Нет описания",
        },
        "en": {
            "help_header": "<tg-emoji emoji-id=5883973610606956186>🗂</tg-emoji> <b>Available modules and commands:</b>\n\n",
            "no_doc": "No description",
        },
    }

    async def _cmd_help(self, message: types.Message) -> None:
        """
         - get available modules and commands
        """
        if message.from_user.id != db.get('tensai.user.telegram_id'):
            return

        text = self.strings("help_header")

        for module_name, module_data in loader.modules.items():
            text += f"<b><tg-emoji emoji-id=5274034223886389748>▫️</tg-emoji> {module_name}</b>\n"

            for cmd_type in ["business_message"]:
                cmds = module_data.get(cmd_type, {})
                for cmd, info in cmds.items():
                    desc = info.get("description", None) or self.strings("no_doc")
                    text += f" ├ <code>{self.prefix}{cmd}</code> <i>{escape_html(desc)}</i>\n"

            text += "\n"

        await message.edit_text(text)