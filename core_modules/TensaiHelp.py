# description: help module
# author: @vsecoder, @fajox

from aiogram import types

from tensai.loader import Module
from tensai.main import loader
from tensai import utils, db
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
            "help_header": "<tg-emoji emoji-id=5883973610606956186>🗂</tg-emoji> <b>Available modules and commands:</b>\n",
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
         - <module name (optional)>- get available modules and commands
        """
        args = utils.get_args(message)
        text = ""

        if args:
            search_query = args.strip()
            module_names = list(loader.modules.keys())
            match = process.extractOne(search_query, module_names, score_cutoff=60)

            if not match:
                await utils.answer(
                    message, self.strings("module_not_found").format(module=search_query)
                )
                return

            module_name, _ = match
            module_data = loader.modules.get(module_name)

            text += f"<b>{module_name}</b>\n"
            handlers = module_data.get("handlers", {})
            commands = handlers.get("command", {})
            bot_commands = handlers.get("bot_command", {})
            inline_commands = handlers.get("inline_command", {})

            text += self._format_commands(commands, bot_commands, inline_commands)

            text = self.strings("module-info").format(
                text,
                module_data.get("description", self.strings("no_doc")),
                module_data.get("author", self.strings("not_mentioned")),
            )

        else:
            text = self.strings("help_header") + "\n"

            for module_name, module_data in loader.modules.items():
                text += f"<b><tg-emoji emoji-id=5274034223886389748>▫️</tg-emoji> {module_name}</b>\n"
                handlers = module_data.get("handlers", {})
                commands = handlers.get("command", {})
                bot_commands = handlers.get("bot_command", {})
                inline_commands = handlers.get("inline_command", {})

                text += self._format_commands(commands, bot_commands, inline_commands)
                text += "\n"

        await utils.answer(message, text)

    def _format_commands(self, commands, bot_commands, inline_commands) -> str:
        lines = []
        all_cmds = list(commands.items())
        all_bot_cmds = list(bot_commands.items())
        all_inline_cmds = list(inline_commands.items())

        bot_username = db.get("tensai.bot.username", "bot")

        for idx, (cmd, info) in enumerate(all_cmds):
            char = "├" if idx < len(all_cmds) - 1 or all_bot_cmds or all_inline_cmds else "└"
            desc = info.get("description") or self.strings("no_doc")
            lines.append(f" {char} <code>{self.get_prefix()}{cmd}</code> <i>{escape_html(desc)}</i>")

        for idx, (cmd, info) in enumerate(all_bot_cmds):
            is_last = (idx == len(all_bot_cmds) - 1 and not all_inline_cmds)
            char = "└" if is_last else "├"
            desc = info.get("description") or self.strings("no_doc")
            lines.append(f" {char} <tg-emoji emoji-id=5931415565955503486>🤖</tg-emoji> <code>/{cmd}</code> <i>{escape_html(desc)}</i>")

        for idx, (cmd, info) in enumerate(all_inline_cmds):
            char = "└" if idx == len(all_inline_cmds) - 1 else "├"
            desc = info.get("description") or self.strings("no_doc")
            lines.append(f" {char} <tg-emoji emoji-id=5931415565955503486>🤖</tg-emoji> <code>@{bot_username} {cmd}</code> <i>{escape_html(desc)}</i>")

        return "\n".join(lines)