from aiogram import types

from tensai import db

import os
import git
import random
import contextlib

def get_prefix() -> str:
    settings: str | None = db.get('tensai.settings', None)
    if not settings:
        db.set('tensai.settings', {'prefix': '.'})
        return '.'
    return settings.get('prefix', '.')

def get_lang() -> str:
    settings: str | None = db.get('tensai.settings', None)
    if not settings:
        db.set('tensai.settings', {'lang': 'en'})
        return '.'
    return settings.get('lang', 'en')

async def get_git_info() -> dict:
    repo: git.Repo = git.Repo(search_parent_directories=True)
    git_dir: str = os.path.join(os.getcwd(), ".git")
    if not os.path.isdir(git_dir):
        raise FileNotFoundError("Not a git repository")

    with open(os.path.join(git_dir, "HEAD"), "r") as head_file:
        ref_line: str = head_file.readline().strip()
        if ref_line.startswith("ref:"):
            branch: str | None = ref_line.split("/")[-1]
            ref_path: str | None = os.path.join(git_dir, *ref_line.split(" ")[1].split("/"))
        else:
            branch: str | None = None
            ref_path: str | None = None
    
    repo.git.fetch()

    if ref_path and os.path.isfile(ref_path):
        with open(ref_path, "r") as ref_file:
            last_commit: str | None = ref_file.readline().strip()
    elif ref_line:
        last_commit: str | None = ref_line.strip()
    else:
        last_commit: str | None = None

    last_commit_short: str | None = last_commit[:7] if last_commit else None

    return {
        "branch": branch,
        "stable_branch": "master",
        "last_commit": last_commit,
        "last_commit_short": last_commit_short
    }

def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def get_args(message: types.Message) -> str:
    """Get arguments from message."""
    
    return args[1] if len(args := message.split(maxsplit=1)) > 1 else ""

def get_base_dir() -> str:
    """Get directory of this file."""

    return os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

def get_platform() -> dict:
    """Returns platform name"""

    with contextlib.suppress(Exception):
        if os.path.isfile("/proc/device-tree/model"):
            with open("/proc/device-tree/model") as f:
                model = f.read()
                return model

    platforms = {
        "HIKKAHOST": {
            "emoji": "🌒",
            "premium_emoji": "",
            "name": "HikkaHost"
        },
        "WSL": {
            "emoji": "💠",
            "premium_emoji": "",
            "name": "WSL"
        },
        "DOCKER": {
            "emoji": "🐳",
            "premium_emoji": "",
            "name": "Docker"
        },
        "CODESPACES": {
            "emoji": random.choice(["🐈‍⬛", "🐙"]),
            "premium_emoji": "",
            "name": "Codespaces"
        },
    }

    for key in platforms:
        if os.environ.get(key):
            return platforms[key]

    return {
        "emoji": "💻",
        "premium_emoji": "",
        "name": "VDS"
    }