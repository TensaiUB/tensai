# description: help module
# author: @vsecoder, @fajox

from aiogram import types

from tensai.loader import Module
from tensai.main import loader
from tensai import utils
from tensai.utils import escape_html

from fuzzywuzzy import process

class TensaiHelp(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "help_header": "<tg-emoji emoji-id=5883973610606956186>🗂</tg-emoji> <b>Доступные модули и команды:</b>\n\n",
            "no_doc": "Нет описания",
            "module_not_found": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Модуль не найден.</b>",
            "not_mentioned": "Не указан",

            "module-info": """<b><tg-emoji emoji-id=5785058280397082578>📁</tg-emoji> Модуль</b> {}
<i><tg-emoji emoji-id=5879785854284599288>ℹ️</tg-emoji> {}</i>

<b><tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji>Developer:</b> <code>{}</code>"""
        },
        "en": {
            "help_header": "<tg-emoji emoji-id=5883973610606956186>🗂</tg-emoji> <b>Available modules and commands:</b>\n\n",
            "no_doc": "No description",
            "module_not_found": "<b><tg-emoji emoji-id=6030331836763213973>❌</tg-emoji> Module not found.</b>",
            "not_mentioned": "Not mentioned",

            "module-info": """<b><tg-emoji emoji-id=5785058280397082578>📁</tg-emoji> Module</b> {}
<i><tg-emoji emoji-id=5879785854284599288>ℹ️</tg-emoji> {}</i>

<b><tg-emoji emoji-id=5190458330719461749>🧑‍💻</tg-emoji>Developer:</b> <code>{}</code>"""
        },
    }

    async def _cmd_help(self, message: types.Message) -> None:
        """
        <module name (optional)>- get available modules and commands
    """
        args = utils.get_args(message) 
        text = ""

        if args:
            search_query = args.strip()

            module_names = list(loader.modules.keys())
            match = process.extractOne(search_query, module_names, score_cutoff=60)

            if not match:
                await utils.answer(message, self.strings("module_not_found").format(module=search_query))
                return

            module_name, score = match
            module_data = loader.modules.get(module_name)

            text += f"<b>{module_name}</b>\n"
            handlers = module_data.get("handlers", {})
            commands = handlers.get("command", {})

            cmds_list = list(commands.items())
            for i, (cmd, info) in enumerate(cmds_list):
                char = "└" if i == len(cmds_list) - 1 else "├"
                desc = info.get("description") or self.strings("no_doc")
                text += f" {char} <code>{self.get_prefix()}{cmd}</code> <i>{escape_html(desc)}</i>\n"
            
            text = self.strings("module-info").format(text, module_data.get("description", self.strings("no_doc")), module_data.get("author", self.strings("not_mentioned")))
        else:
            text = self.strings("help_header")

            for module_name, module_data in loader.modules.items():
                text += f"<b><tg-emoji emoji-id=5274034223886389748>▫️</tg-emoji> {module_name}</b>\n"

                handlers = module_data.get("handlers", {})
                commands = handlers.get("command", {})

                cmds_list = list(commands.items())

                for i, (cmd, info) in enumerate(cmds_list):
                    char = "└" if i == len(cmds_list) - 1 else "├"
                    desc = info.get("description") or self.strings("no_doc")
                    text += f" {char} <code>{self.get_prefix()}{cmd}</code> <i>{escape_html(desc)}</i>\n"

                text += "\n"

        await utils.answer(message, text)