from aiogram import types
from tensai import utils
from tensai.loader import Module
import asyncio
import os
import hashlib
import time


def hash_msg(message):
    return hashlib.sha256(message.text.encode("utf-8")).hexdigest()


class Tensaiteminal(Module):
    strings: dict[str, dict[str, str]] = {
        "ru": {
            "running": "<b>⌨️ Системная команда:</b>\n<pre><code class='language-bash'>{command}</code></pre>",
            "status_running": "\n\n<b>Запуск...</b>",
            "finished": "\n\n<b>✔️ Код выхода:</b> <code>{exit_code}</code>",
            "stdout": "\n\n<b>📼 Stdout:</b>\n<pre><code class='language-bash'>{stdout}</code></pre>",
            "stderr": "\n\n<b>🚫 Stderr:</b>\n<pre><code class='language-bash'>{stderr}</code></pre>",
            "done": "<b>✅ Команда выполнена успешно.</b>",
            "what_to_kill": "<b>❌ Ответьте на сообщение с командой, которую хотите завершить.</b>",
            "kill_fail": "<b>❌ Не удалось завершить процесс.</b>",
            "killed": "<b>✅ Процесс завершен.</b>",
            "no_cmd": "<b>❌ Указанная команда не активна.</b>",
        },
        "en": {
            "running": "<b>⌨️ System Command:</b>\n<pre><code class='language-bash'>{command}</code></pre>",
            "status_running": "\n\n<b>Running...</b>",
            "finished": "\n\n<b>✔️ Exit Code:</b> <code>{exit_code}</code>",
            "stdout": "\n\n<b>📼 Stdout:</b>\n<pre><code class='language-bash'>{stdout}</code></pre>",
            "stderr": "\n\n<b>🚫 Stderr:</b>\n<pre><code class='language-bash'>{stderr}</code></pre>",
            "done": "<b>✅ Command finished successfully.</b>",
            "what_to_kill": "<b>❌ Reply to the command message you want to terminate.</b>",
            "kill_fail": "<b>❌ Failed to terminate the process.</b>",
            "killed": "<b>✅ Process terminated.</b>",
            "no_cmd": "<b>❌ No active command found.</b>",
        },
    }

    def __init__(self):
        super().__init__()
        self.activecmds = {}
        self.message_buffers = {}
        self.last_update_time = 0

    async def _cmd_terminal(self, message: types.Message):
        """<command> - execute shell command"""
        command = utils.get_args(message)
        if not command:
            return await utils.answer(
                message, "<b>❌ Укажите команду для выполнения.</b>"
            )
        await self.run_command(message, command)

    async def _cmd_apt(self, message: types.Message):
        """<command> - execute apt command (with sudo if needed)"""
        command = utils.get_args(message)
        cmd = f"apt {command} -y" if os.geteuid() == 0 else f"sudo -S apt {command} -y"
        await self.run_command(message, cmd)

    async def _cmd_terminate(self, message: types.Message):
        """<command> - terminate running command"""
        if not message.is_reply:
            return await utils.answer(message, self.strings("what_to_kill"))

        reply_msg = await message.get_reply_message()
        msg_hash = hash_msg(reply_msg)

        if msg_hash in self.activecmds:
            try:
                self.activecmds[msg_hash].terminate()
                del self.message_buffers[msg_hash]
            except Exception:
                return await utils.answer(message, self.strings("kill_fail"))
            else:
                return await utils.answer(message, self.strings("killed"))
        else:
            return await utils.answer(message, self.strings("no_cmd"))

    async def run_command(self, message: types.Message, cmd: str):
        sproc = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=utils.get_base_dir(),
        )

        msg_hash = hash_msg(message)
        self.activecmds[msg_hash] = sproc
        self.message_buffers[msg_hash] = {
            "base_text": self.strings("running").format(command=utils.escape_html(cmd)),
            "stdout": "",
            "stderr": "",
            "message": None,
            "last_update": 0,
            "status": self.strings("status_running"),
            "first_update": True,
        }

        await self.send_output(message, sproc, msg_hash)

    async def send_output(
        self, message: types.Message, sproc: asyncio.subprocess.Process, msg_hash: str
    ):
        buffer = self.message_buffers[msg_hash]

        initial_message = buffer["base_text"] + buffer["status"]
        buffer["message"] = await utils.answer(message, initial_message)

        stdout_task = asyncio.create_task(
            self.read_stream(sproc.stdout, msg_hash, "stdout")
        )
        stderr_task = asyncio.create_task(
            self.read_stream(sproc.stderr, msg_hash, "stderr")
        )

        await asyncio.gather(stdout_task, stderr_task)
        exit_code = await sproc.wait()

        parts = [buffer["base_text"]]

        if buffer["stdout"]:
            parts.append(
                self.strings("stdout").format(
                    stdout=utils.escape_html(buffer["stdout"])
                )
            )

        if buffer["stderr"]:
            parts.append(
                self.strings("stderr").format(
                    stderr=utils.escape_html(buffer["stderr"])
                )
            )

        parts.append(self.strings("finished").format(exit_code=exit_code))

        await utils.answer(buffer["message"], "".join(parts))

        del self.activecmds[msg_hash]
        del self.message_buffers[msg_hash]

    async def read_stream(self, stream, msg_hash: str, stream_type: str):
        buffer = self.message_buffers[msg_hash]
        update_interval = 3
        min_chars_for_update = 100

        while True:
            line = await stream.readline()
            if not line:
                break

            decoded_line = line.decode(errors="replace").rstrip()
            buffer[stream_type] += decoded_line + "\n"

            current_time = time.time()
            time_since_last = current_time - buffer["last_update"]
            new_chars = len(decoded_line)

            if buffer["first_update"] or (
                time_since_last >= update_interval and new_chars >= min_chars_for_update
            ):

                await self.update_message(msg_hash)
                buffer["last_update"] = current_time
                buffer["first_update"] = False

        await self.update_message(msg_hash)

    async def update_message(self, msg_hash: str):
        buffer = self.message_buffers[msg_hash]
        if not buffer["message"]:
            return

        parts = [buffer["base_text"]]

        if buffer["stdout"]:
            parts.append(
                self.strings("stdout").format(
                    stdout=utils.escape_html(buffer["stdout"])
                )
            )

        if buffer["stderr"]:
            parts.append(
                self.strings("stderr").format(
                    stderr=utils.escape_html(buffer["stderr"])
                )
            )

        if not buffer["stdout"] and not buffer["stderr"]:
            parts.append(buffer["status"])

        try:
            await utils.answer(buffer["message"], "".join(parts))
        except Exception:
            pass
