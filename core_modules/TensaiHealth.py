# description: comprehensive health check module
# author: @vsecoder, @fajox

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import git
import time
import psutil
import platform
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError, RedisError
from typing import Dict, Any

from tensai import start_time, utils, db
from tensai.loader import Module


class TensaiHealth(Module):
    strings: dict[str, dict[str, str]] = {
        "en": {
            "health_header": "📊 <b>System Health</b>",
            "health_stats": "<blockquote expandable>{stats}</blockquote>",
            "uptime": "⏱ <b>Uptime:</b> <code>{uptime}</code>",
            "ping": "🏓 <b>Ping:</b> <code>{ping} ms</code>",
            "version": "🔖 <b>Version:</b> <code>{version}</code>",
            "branch": "🌿 <b>Branch:</b> <code>{branch}</code>",
            "commit": "🔑 <b>Commit:</b> <code>{commit}</code>",
            "up_to_date": "✅ <b>Up to date</b>",
            "update_available": "🔄 <b>Update available!</b>",
            "system": "💻 <b>System:</b> <code>{system}</code>",
            "cpu": "⚙️ <b>CPU (bot):</b> <code>{cpu_usage}%</code>",
            "ram": "🧠 <b>RAM (bot):</b> <code>{ram_usage} MB</code>",
            "disk": "💾 <b>Disk:</b> <code>{disk_usage}%</code>",
            "redis": "🗃 <b>Redis:</b> {status}",
            "rights_header": "🔐 <b>Rights</b>",
            "rights_stats": "<blockquote expandable>{stats}</blockquote>",
            "rights_item": "<code>{right}:</code> {value}",
            "rights_last_item": "<code>{right}:</code> {value}",
            "true": "✅",
            "false": "❌",
            "rights_desc": "<i>{desc}</i>",
            "rights_descriptions": {
                "can_reply": "Can reply to messages in private chats",
                "can_read_messages": "Can mark incoming messages as read",
                "can_delete_outgoing_messages": "Can delete messages sent by the bot",
                "can_delete_all_messages": "Can delete all messages in managed chats",
                "can_edit_name": "Can edit business account name",
                "can_edit_bio": "Can edit business account bio",
                "can_edit_profile_photo": "Can edit business account profile photo",
                "can_edit_username": "Can edit business account username",
                "can_change_gift_settings": "Can change gift privacy settings",
                "can_view_gifts_and_stars": "Can view gifts and Stars",
                "can_convert_gifts_to_stars": "Can convert gifts to Stars",
                "can_transfer_and_upgrade_gifts": "Can transfer and upgrade gifts",
                "can_transfer_stars": "Can transfer Stars",
                "can_manage_stories": "Can manage stories",
            },
        },
    }

    async def _cmd_health(self, message: types.Message) -> None:
        """
        - comprehensive system health check
        """
        stats = []

        # Ping
        ping = await self.get_ping(message)
        stats.append(self.strings("ping").format(ping=ping))

        # Uptime
        uptime = self.get_uptime()
        stats.append(self.strings("uptime").format(uptime=uptime))

        # Git info
        git_info = await self.get_git_info()
        stats.extend(
            [
                self.strings("version").format(version=git_info["version"]),
                self.strings("branch").format(branch=git_info["branch"]),
                self.strings("commit").format(commit=git_info["commit"]),
                git_info["update_status"],
            ]
        )

        # System info
        sys_info = self.get_system_info()
        stats.extend(
            [
                self.strings("system").format(system=sys_info["system"]),
                self.strings("cpu").format(cpu_usage=sys_info["cpu"]),
                self.strings("ram").format(ram_usage=sys_info["ram"]),
                self.strings("disk").format(disk_usage=sys_info["disk"]),
            ]
        )

        # Redis status
        redis_status = await self.get_redis_status()
        stats.append(self.strings("redis").format(status=redis_status))

        # Compose main stats with box borders
        health_text = (
            self.strings("health_header")
            + "\n"
            + self.strings("health_stats").format(stats="\n".join(stats))
        )

        # Rights section
        rights = self.get_rights()
        rights_text = [self.strings("rights_header")]
        rights_items = list(rights.items())

        for i, (right, value) in enumerate(rights_items):
            desc = self.strings("rights_descriptions").get(right, "")
            template = self.strings(
                "rights_last_item" if i == len(rights_items) - 1 else "rights_item"
            )

            rights_text.append(
                template.format(
                    right=right,
                    value=self.strings("true") if value else self.strings("false"),
                )
            )
            if desc:
                rights_text.append(self.strings("rights_desc").format(desc=desc))

        rights_section = (
            self.strings("rights_stats").format(stats="\n".join(rights_text))
        )

        # Combine all sections
        full_message = health_text + "\n\n" + rights_section

        # Add update button if update available
        if not git_info["is_up_to_date"]:
            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                types.InlineKeyboardButton(
                    text=self.strings("update_button"),
                    callback_data="tensai_update",
                )
            )
            await utils.answer(message, full_message, reply_markup=keyboard.as_markup())
        else:
            await utils.answer(message, full_message)

    async def get_ping(self, message: types.Message) -> int:
        """Calculate ping to Telegram servers"""
        start = time.monotonic()
        await utils.answer(message, "🏓")
        end = time.monotonic()
        return int((end - start) * 1000)

    def get_uptime(self) -> str:
        """Get formatted uptime"""
        uptime = time.time() - start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"

    async def get_git_info(self) -> Dict[str, Any]:
        """Get git repository information"""
        try:
            repo = git.Repo(search_parent_directories=True)
            origin = repo.remotes.origin
            origin.fetch()

            local_commit = repo.head.commit.hexsha[:7]
            remote_commit = repo.refs[
                f"origin/{repo.active_branch.name}"
            ].commit.hexsha[:7]

            # Try to get version from tags
            try:
                version = repo.git.describe("--tags")
            except Exception:
                version = "untagged"

            is_up_to_date = local_commit == remote_commit
            update_status = (
                self.strings("up_to_date")
                if is_up_to_date
                else self.strings("update_available")
            )

            return {
                "version": version,
                "branch": repo.active_branch.name,
                "commit": local_commit,
                "is_up_to_date": is_up_to_date,
                "update_status": update_status,
            }
        except Exception as e:
            print(f"Git error: {e}")
            return {
                "version": "unknown",
                "branch": "unknown",
                "commit": "unknown",
                "is_up_to_date": True,
                "update_status": self.strings("up_to_date"),
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system resource usage"""
        process = psutil.Process()
        disk_usage = psutil.disk_usage("/").percent

        # Get system-wide CPU usage if possible
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
        except Exception:
            cpu_usage = process.cpu_percent(interval=0.1)

        return {
            "system": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "cpu": round(cpu_usage, 1),
            "ram": round(process.memory_info().rss / (1024 * 1024), 1),  # MB
            "disk": disk_usage,
        }

    async def get_redis_status(self) -> str:
        """Check Redis connection status"""
        try:
            redis_client = Redis(
                host="localhost",
                port=6379,
                password=None,
                decode_responses=True,
                socket_timeout=1,
                socket_connect_timeout=1,
            )
            if await redis_client.ping():
                # Get some basic Redis info
                info = redis_client.info()
                return f"✅ {info['redis_version']} (used_memory: {info['used_memory_human']})"
            return "❌ Ping failed"
        except (RedisConnectionError, RedisError, OSError):
            return "❌ Disconnected (using fake Redis)"

    def get_rights(self) -> Dict[str, bool]:
        """Get current rights dictionary with all possible rights"""
        all_rights = {
            "can_reply": False,
            "can_read_messages": False,
            "can_delete_outgoing_messages": False,
            "can_delete_all_messages": False,
            "can_edit_name": False,
            "can_edit_bio": False,
            "can_edit_profile_photo": False,
            "can_edit_username": False,
            "can_change_gift_settings": False,
            "can_view_gifts_and_stars": False,
            "can_convert_gifts_to_stars": False,
            "can_transfer_and_upgrade_gifts": False,
            "can_transfer_stars": False,
            "can_manage_stories": False,
        }

        # Update with actual values from DB
        db_rights = db.get("tensai.rights", {})
        for right in all_rights:
            if right in db_rights:
                all_rights[right] = bool(db_rights[right])

        return all_rights
