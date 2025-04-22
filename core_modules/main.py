# description: tensai module
# author: @vsecoder

from aiogram import types
from tensai.loader import Module
from tensai import db
from tensai.update import update
import git


class Main(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "info": (
                "<blockquote>Tensai - так называют робота, который знает всё и умеет всё.\n"
                "Он использует Telegram Bussiness API, поэтому не нарушает никаких правил.\n"
                "Но работает он только в ЛС, так что используется для бизнеса.</blockquote>\n"
            ),
        },
        "en": {
            "info": (
                "<blockquote>Tensai - so-called robot who knows everything and can do everything.\n"
                "He uses Telegram Bussiness API, so he doesn't break any rules.\n"
                "But he works only in private chat, so he is used for business.</blockquote>\n"
            )
        },
    }

    async def _cmd_tensai(self, message: types.Message) -> None:
        """
         - get info
        """
        if message.from_user.id != db.get('tensai.user.telegram_id'):
            return

        await message.edit_text(self.strings("info"))

    async def _cmd_update(self, message: types.Message) -> None:
        """
         - update tensai
        """
        if message.from_user.id != db.get("tensai.user.telegram_id"):
            return

        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin

        origin.fetch()

        local_commit = repo.head.commit.hexsha
        remote_commit = repo.refs[f"origin/{repo.active_branch.name}"].commit.hexsha

        if local_commit != remote_commit:
            await message.edit_text("New update available, updating...")
            await update(origin)
        else:
            await message.edit_text("No new update available.")
