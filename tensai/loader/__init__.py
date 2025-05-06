# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

from types import ModuleType
from pathlib import Path
from importlib.machinery import ModuleSpec

from aiogram import Router, F
from aiogram.types import Message, InlineQuery, CallbackQuery
from tensai import dp, utils, db
from tensai.loader.decorators import Decorators

import os
import sys
import inspect
import asyncio
import subprocess
import logging
import importlib.util

logger = logging.getLogger(__name__)


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


class Loader(Decorators):
    def __init__(self) -> None:
        self.core_modules_dir = Path("core_modules")
        self.modules_dir = Path("modules")
        self.modules: dict = {}

        self.cmd_handlers = []
        self.botcmd_handlers = []
        self.inline_handlers = []
        self.inlinecmd_handlers = []
        self.botmsg_handlers = []
        self.cbq_handlers = []
        self.bismsg_handlers = []
        self.bisedit_handlers = []
        self.bisdel_handlers = []

        self.router = Router()

        self._register_base_handlers()
        dp.include_router(self.router)

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
        # Loads module and adds it's handlers in relevant lists
        try:
            requires = self._parse_metadata(module_path, ["requires"]).get("requires")
            if requires:
                print("Installing module's requirements...")
                logger.info(f"Installing {module_path}'s requirements: {requires}")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", *requires.split(", ")]
                )

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
                logger.error(f"Module class not found in {module_name}")
                print(f"Module class not found in {module_name}")
                return

            instance = module_class()
            module_handlers = {}

            for attr_name in dir(instance):
                handler = getattr(instance, attr_name)
                if not callable(handler):
                    continue

                # Проверяем наличие метаданных от декоратора
                handler_meta = getattr(handler, "_handler_meta", None)

                if attr_name == "on_load":
                    if asyncio.iscoroutinefunction(handler):
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(handler())
                        except RuntimeError:
                            asyncio.run(handler())
                    else:
                        handler()
                    continue

                if handler_meta:
                    # Обработка декорированных функций
                    handler_type = handler_meta["type"]
                    if handler_type == "command":
                        self.cmd_handlers.append(handler)
                    elif handler_type == "bot_command":
                        self.botcmd_handlers.append(handler)
                    elif handler_type == "inline_command":
                        self.inlinecmd_handlers.append(handler)
                    elif handler_type == "inline":
                        self.inline_handlers.append(handler)
                    elif handler_type == "bot_message":
                        self.botmsg_handlers.append(handler)
                    elif handler_type == "callback_query":
                        self.cbq_handlers.append(handler)
                    elif handler_type == "business_message":
                        self.bismsg_handlers.append(handler)
                    elif handler_type == "edited_business_message":
                        self.bisedit_handlers.append(handler)
                    elif handler_type == "deleted_business_message":
                        self.bisdel_handlers.append(handler)

                    # Добавляем информацию о хендлере в module_handlers
                    if handler_type not in module_handlers:
                        module_handlers[handler_type] = {}

                    name = attr_name.split("_", 2)[-1] if "_" in attr_name else attr_name
                    doc = handler_meta.get("description") or inspect.getdoc(handler) or ""

                    module_handlers[handler_type][name] = {
                        "handler": handler,
                        "description": doc,
                        "aliases": handler_meta.get("aliases", []),
                    }
                else:
                    # Старая логика для совместимости
                    handler_type = ""
                    if attr_name.startswith("_cmd_"):
                        self.cmd_handlers.append(handler)
                        handler_type = "command"
                    elif attr_name.startswith("_botcmd_"):
                        self.botcmd_handlers.append(handler)
                        handler_type = "bot_command"
                    elif attr_name.startswith("_inlinecmd_"):
                        self.inlinecmd_handlers.append(handler)
                        handler_type = "inline_command"
                    elif attr_name.startswith("_inline_"):
                        self.inline_handlers.append(handler)
                        handler_type = "inline"
                    elif attr_name.startswith("_botmsg_"):
                        self.botmsg_handlers.append(handler)
                        handler_type = "bot_message"
                    elif attr_name.startswith("_cbq_"):
                        self.cbq_handlers.append(handler)
                        handler_type = "callback_query"
                    elif attr_name.startswith("_bismsg_"):
                        self.bismsg_handlers.append(handler)
                        handler_type = "business_message"
                    elif attr_name.startswith("_bisedit_"):
                        self.bisedit_handlers.append(handler)
                        handler_type = "edited_business_message"
                    elif attr_name.startswith("_bisdel_"):
                        self.bisdel_handlers.append(handler)
                        handler_type = "deleted_business_message"

                    if handler_type:
                        name = (
                            attr_name.split("_", 2)[-1] if "_" in attr_name else attr_name
                        )
                        doc = inspect.getdoc(handler) or ""

                        if handler_type not in module_handlers:
                            module_handlers[handler_type] = {}

                        module_handlers[handler_type][name] = {
                            "handler": handler,
                            "description": doc,
                            "aliases": [],
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

            print(f"Module {module_name} loaded and handlers registered!")
            logger.info(f"Module {module_name} loaded and handlers registered")

        except Exception as e:
            print(f"Error loading module {module_path.stem}: {e}")
            logger.error(f"Error loading module {module_path.stem}: {e}")

    def _load_modules(self):
        # Loads all modules from core_modules and modules dirs
        for path in [self.core_modules_dir, self.modules_dir]:
            for file in path.glob("*.py"):
                if not file.name.startswith("_"):
                    self.load_module(file, core=(path == self.core_modules_dir))
            logger.info(f"Loaded modules from {path}")

    def unload_module(self, module_name: str):
        # Deletes module from memory and file system
        os.remove(self.modules_dir / f"{module_name}.py")
        self.modules.pop(module_name, None)
        logger.info(f"Module {module_name} unloaded")
