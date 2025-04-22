import os
import sys
import asyncio
import git

from tensai import bot, db


async def update(origin):
    origin.pull()
    os.execv(sys.executable, [sys.executable, *sys.argv])


async def auto_updater():
    while True:
        await asyncio.sleep(300)
        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin

        origin.fetch()

        local_commit = repo.head.commit.hexsha
        remote_commit = repo.refs[f"origin/{repo.active_branch.name}"].commit.hexsha

        if local_commit != remote_commit:
            owner = db.get("tensai.user.telegram_id")
            await bot.send_message(owner, "New update available!")
