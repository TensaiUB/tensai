import os
import sys
import asyncio
import git
import signal
import atexit

from tensai import bot, db
from rich import print

def get_startup_callback() -> callable:
    """
    Возвращает функцию, которая перезапускает скрипт при вызове.
    За первоисточник взят данный код:
    https://github.com/hikariatama/Hikka/blob/35bd52e24026bb6cb6e7a4ef2f85e9ca900b16aa/hikka/_internal.py#L20
    """
    return lambda *_: os.execl(
        sys.executable,
        sys.executable,
        "-m",
        os.path.relpath(
            os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        ),
        *sys.argv[1:],
    )

def die():
    """Метод для завершения текущего процесса."""
    if "DOCKER" in os.environ:
        sys.exit(0)
    elif os.name == "nt":
        sys.exit(0)
    else:
        os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)


def restart():
    if db.get("tensai.restart.do_not_restart", None):
        print("⚠️ Restart aborted due to DO_NOT_RESTART environment variable")
        sys.exit(0)

    print("🔄 Restarting...")

    db.set("tensai.restart.do_not_restart", "42")

    if "DOCKER" in os.environ or os.name == "nt":
        atexit.register(get_startup_callback())
    else:
        signal.signal(signal.SIGTERM, get_startup_callback())

    die()

async def update(origin):
    origin.pull()
    await restart()

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
