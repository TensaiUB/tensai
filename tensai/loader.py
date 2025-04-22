import os
import inspect
import importlib.util
from types import ModuleType
from pathlib import Path
from importlib.machinery import ModuleSpec

from aiogram import Router, F
from tensai import dp, utils


class Strings:
    def __init__(self, strings: dict) -> None:
        self._strings = strings

    def __call__(self, name: str) -> str:
        lang = utils.get_lang()
        return self._strings.get(lang, {}).get(name) or self._strings.get("en", {}).get(name, name)


class Module:
    strings: dict[str, dict[str, str]] = {}

    def __init__(self) -> None:
        self.prefix = utils.get_prefix()
        self.lang = utils.get_lang()
        self.strings = Strings(self.strings)

    async def on_load(self) -> None:
        pass


class Loader:
    def __init__(self) -> None:
        self.core_modules_dir = Path("core_modules")
        self.modules_dir = Path("modules")

        self.modules: dict = {}

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
        try:
            spec: ModuleSpec = importlib.util.spec_from_file_location(
                f"{'core_' if core else ''}modules.{module_path.stem}", module_path
            )
            module: ModuleType = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            module_name = module_path.stem.capitalize()
            module_class = next(
                (obj for name, obj in inspect.getmembers(module, inspect.isclass) if name.lower() == module_name.lower()), None
            )
            if not module_class:
                print(f"Module class not found in {module_name}")
                return

            instance = module_class()
            router = Router(name=module_name)

            handlers_by_type = {
                "_cmd_": (
                    "business_message",
                    lambda cmd: F.text.startswith(f"{instance.prefix}{cmd}"),
                ),
                "_inline_": ("inline_query", lambda _: True),
                "_cbq_": ("callback_query", lambda _: True),
                "_bismsg_": ("business_message", lambda _: F.from_user),
                "_bisedit_": ("business_edited_message", lambda _: True),
                "_bisdel_": ("business_deleted_message", lambda _: True),
            }

            handlers = {k: {} for k, _ in handlers_by_type.values()}

            for attr_name in dir(instance):
                handler = getattr(instance, attr_name)
                if not callable(handler):
                    continue

                for prefix, (handler_type, filter_fn) in handlers_by_type.items():
                    if attr_name.startswith(prefix):
                        cmd = attr_name.replace(prefix, "")
                        doc = inspect.getdoc(handler) or ""
                        if handler_type == "inline_query":
                            router.inline_query()(handler)
                        elif handler_type == "callback_query":
                            router.callback_query()(handler)
                        elif handler_type == "business_message":
                            router.business_message(filter_fn(cmd))(handler)
                        elif handler_type == "business_edited_message":
                            router.edited_business_message()(handler)
                        elif handler_type == "business_deleted_message":
                            router.deleted_business_messages()(handler)

                        handlers[handler_type][cmd] = {"handler": handler, "description": doc}
                        break

            self.modules[module_name] = {
                "name": module_name,
                "router": router,
                **handlers,
                **self._parse_metadata(module_path, ["description", "author", "version", "requirements", "ba"]),
            }

            dp.include_router(router)
            print(f"Module {module_name} loaded and router registered!")

        except Exception as e:
            print(f"Error loading module {module_path.stem}: {e}")

    def _load_modules(self):
        for path in [self.core_modules_dir, self.modules_dir]:
            for file in path.glob("*.py"):
                if not file.name.startswith("_"):
                    self.load_module(file, core=(path == self.core_modules_dir))

    def unload_module(self, module_name: str):
        os.remove(self.modules_dir / f"{module_name}.py")
        self.modules.pop(module_name, None)