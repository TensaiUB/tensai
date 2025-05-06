# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

import os
import sys
import signal
import atexit
import logging

from tensai import db
from rich import print


logger = logging.getLogger(__name__)

def get_startup_callback() -> callable:
    """
    Returns function, that restarts script at call.
    First source has been taken from:
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
    """Method that stops current process."""
    if "DOCKER" in os.environ or os.name == "nt":
        sys.exit(0)
    else:
        os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)

def restart():
    if db.get("tensai.restart.do_not_restart", None):
        print("⚠️ Restart aborted due to DO_NOT_RESTART environment variable")
        sys.exit(0)

    print("🔄 Restarting...")
    logger.info("Restarting...")

    db.set("tensai.restart.do_not_restart", "42")

    if "DOCKER" in os.environ or os.name == "nt":
        atexit.register(get_startup_callback())
    else:
        signal.signal(signal.SIGTERM, get_startup_callback())

    die()
