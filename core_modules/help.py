# description: help module
# author: @vsecoder

from aiogram import types
from tensai.loader import Module
from tensai import db
from tensai.main import loader
from tensai.utils import get_prefix, escape_html


class Help(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "help_header": "🧩 <b>Доступные модули и команды:</b>\n\n",
            "no_doc": "Нет описания",
        },
        "en": {
            "help_header": "🧩 <b>Available modules and commands:</b>\n\n",
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
        prefix = get_prefix()

        for module_name, module_data in loader.modules.items():
            text += f"<b>📦 {module_name}</b>\n"

            for cmd_type in ["business_message"]:
                cmds = module_data.get(cmd_type, {})
                for cmd, info in cmds.items():
                    desc = info.get("description", "") or self.strings("no_doc")
                    text += f" ├ <code>{prefix}{cmd}</code> <i>{escape_html(desc)}</i>\n"

            text += "\n"

        await message.edit_text(text)
