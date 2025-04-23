from types import ModuleType
from pathlib import Path
from importlib.machinery import ModuleSpec

from aiogram import Router
from aiogram.types import Message, InlineQuery, CallbackQuery
from tensai import dp, utils, db

import os
import sys
import inspect
import asyncio
import subprocess
import importlib.util

class Strings:
    def __init__(self, strings: dict) -> None:
        self._strings = strings

    def __call__(self, name: str) -> str:
        lang = utils.get_lang()
        return self._strings.get(lang, {}).get(name) or self._strings.get("en", {}).get(
            name, name
        )


class Module:
    strings: dict[str, dict[str, str]] = {}

    def __init__(self) -> None:
        self.get_prefix = utils.get_prefix
        self.lang = utils.get_lang()
        self.strings = Strings(self.strings)

    async def on_load(self) -> None:
        pass


class Loader:
    def __init__(self) -> None:
        self.core_modules_dir = Path("core_modules")
        self.modules_dir = Path("modules")
        self.modules: dict = {}
        self.cmd_handlers = []
        self.inline_handlers = []
        self.cbq_handlers = []
        self.bismsg_handlers = []
        self.bisedit_handlers = []
        self.bisdel_handlers = []
        self.router = Router()
        self._register_base_handlers()
        dp.include_router(self.router)

    def _register_base_handlers(self):
        # Регистрирует основной роутер и хендлеры по видам событий
        @self.router.business_message()
        async def handle_business_message(message: Message):
            prefix = utils.get_prefix()
            user_id = db.get("tensai.user.telegram_id")
            for handler in self.cmd_handlers:
                if not getattr(message, "text", ""):
                    continue

                name = handler.__name__.replace("_cmd_", "")
                if (
                    message.text.startswith(f"{prefix}{name}")
                    and message.from_user.id == user_id
                ):
                    await handler(message)
            for handler in self.bismsg_handlers:
                await handler(message)

        @self.router.edited_business_message()
        async def handle_edited_message(message: Message):
            for handler in self.bisedit_handlers:
                await handler(message)

        @self.router.deleted_business_messages()
        async def handle_deleted_message(message: Message):
            for handler in self.bisdel_handlers:
                await handler(message)

        @self.router.inline_query()
        async def handle_inline_query(query: InlineQuery):
            for handler in self.inline_handlers:
                await handler(query)

        @self.router.callback_query()
        async def handle_callback_query(query: CallbackQuery):
            for handler in self.cbq_handlers:
                await handler(query)

    def _parse_metadata(self, module_path: Path, keys: list[str]) -> dict:
        meta = {}
        with open(module_path, encoding="utf-8") as file:
            for line in file:
                if line.startswith("# "):
                    parts = line[2:].strip().split(":", 1)
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        if key in keys:
                            meta[key] = value
        return meta

    def load_module(self, module_path: Path, core: bool = False) -> None:
        # Загружает модуль и добавляет его хендлеры в соответствующие списки
        try:
            spec: ModuleSpec = importlib.util.spec_from_file_location(
                f"{'core_' if core else ''}modules.{module_path.stem}", module_path
            )
            module: ModuleType = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            module_name = module_path.stem.capitalize()
            module_class = next(
                (
                    obj
                    for name, obj in inspect.getmembers(module, inspect.isclass)
                    if name.lower() == module_name.lower()
                ),
                None,
            )
            if not module_class:
                print(f"Module class not found in {module_name}")
                return

            instance = module_class()
            module_handlers = {}

            for attr_name in dir(instance):
                handler = getattr(instance, attr_name)
                if not callable(handler):
                    continue

                handler_type = ""

                if attr_name == "on_load":
                    if asyncio.iscoroutinefunction(handler):
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(handler())
                        except RuntimeError:
                            asyncio.run(handler())
                    else:
                        handler()
                if attr_name.startswith("_cmd_"):
                    self.cmd_handlers.append(handler)
                    handler_type = "command"
                elif attr_name.startswith("_inline_"):
                    self.inline_handlers.append(handler)
                    handler_type = "inline"
                elif attr_name.startswith("_cbq_"):
                    self.cbq_handlers.append(handler)
                    handler_type = "callback query"
                elif attr_name.startswith("_bismsg_"):
                    self.bismsg_handlers.append(handler)
                    handler_type = "business message"
                elif attr_name.startswith("_bisedit_"):
                    self.bisedit_handlers.append(handler)
                    handler_type = "edited business message"
                elif attr_name.startswith("_bisdel_"):
                    self.bisdel_handlers.append(handler)
                    handler_type = "deleted business message"

                name = attr_name.replace(f"_{handler_type}_", "")
                doc = inspect.getdoc(handler) or ""

                if handler_type:
                    name = attr_name.split("_", 2)[-1]
                    doc = inspect.getdoc(handler) or ""

                    if handler_type not in module_handlers:
                        module_handlers[handler_type] = {}

                    module_handlers[handler_type][name] = {
                        "handler": handler,
                        "description": doc,
                    }

            self.modules[module_name] = {
                "name": module_name,
                "core": core,
                "handlers": module_handlers,
                **self._parse_metadata(
                    module_path,
                    ["description", "author", "version", "requires", "ba"],
                ),
            }

            requires = self.modules[module_name].get("requires", False)
            if requires:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *requires.split(", ")])

            print(f"Module {module_name} loaded and handlers registered!")

        except Exception as e:
            print(f"Error loading module {module_path.stem}: {e}")

    def _load_modules(self):
        # Загружает все модули из директорий core_modules и modules
        for path in [self.core_modules_dir, self.modules_dir]:
            for file in path.glob("*.py"):
                if not file.name.startswith("_"):
                    self.load_module(file, core=(path == self.core_modules_dir))

    def unload_module(self, module_name: str):
        # Удаляет модуль из памяти и файловой системы
        os.remove(self.modules_dir / f"{module_name}.py")
        self.modules.pop(module_name, None)
