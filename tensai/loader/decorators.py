from aiogram.types import Message, InlineQuery, CallbackQuery
from tensai import db, utils
from aiogram import F


class Decorators:
    def command(self, aliases=None, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "command",
                "aliases": aliases or [],
                "description": description or {}
            }
            return func
        return decorator

    def bot_command(self, aliases=None, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "bot_command",
                "aliases": aliases or [],
                "description": description or {}
            }
            return func
        return decorator

    def inline_command(self, aliases=None, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "inline_command",
                "aliases": aliases or [],
                "description": description or {}
            }
            return func
        return decorator

    def inline(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "inline",
                "description": description or {}
            }
            return func
        return decorator

    def bot_message(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "bot_message",
                "description": description or {}
            }
            return func
        return decorator

    def callback_query(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "callback_query",
                "description": description or {}
            }
            return func
        return decorator

    def business_message(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "business_message",
                "description": description or {}
            }
            return func
        return decorator

    def edited_business_message(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "edited_business_message",
                "description": description or {}
            }
            return func
        return decorator

    def deleted_business_message(self, description=None):
        def decorator(func):
            func._handler_meta = {
                "type": "deleted_business_message",
                "description": description or {}
            }
            return func
        return decorator

    def _register_base_handlers(self):
        # Register main router and handlers
        @self.router.business_message()
        async def handle_business_message(message: Message):
            prefix = utils.get_prefix()
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.cmd_handlers:
                if not getattr(message, "text", ""):
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                else:
                    names = [handler.__name__.replace("_cmd_", "")]

                if (
                    any(message.text.startswith(f"{prefix}{name}") for name in names)
                    or any(message.text.startswith(f"{prefix} {name}") for name in names)
                ) and (
                    message.from_user.id == user_id or message.from_user.id in owners
                ):
                    await handler(message)

            for handler in self.bismsg_handlers:
                await handler(message)

        @self.router.message(F.text.startswith("/"))
        async def handle_bot_message(message: Message):
            for handler in self.botcmd_handlers:
                if not getattr(message, "text", ""):
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                else:
                    names = [handler.__name__.replace("_botcmd_", "")]

                if any(message.text.split()[0] == f"/{name}" or 
                    message.text.split()[0] == f"/{name}@{message.bot.username}" 
                    for name in names):
                    await handler(message)

        @self.router.edited_business_message()
        async def handle_edited_message(message: Message):
            for handler in self.bisedit_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta or handler_meta.get("type") == "edited_business_message":
                    await handler(message)

        @self.router.deleted_business_messages()
        async def handle_deleted_message(message: Message):
            for handler in self.bisdel_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta or handler_meta.get("type") == "deleted_business_message":
                    await handler(message)

        @self.router.message()
        async def handle_botmsg(message: Message):
            for handler in self.botmsg_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta or handler_meta.get("type") == "bot_message":
                    await handler(message)

        @self.router.inline_query(F.query)
        async def handle_inlinecmd_query(query: InlineQuery):
            for handler in self.inlinecmd_handlers:
                if not query.query:
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                else:
                    names = [handler.__name__.replace("_inlinecmd_", "")]

                if any(query.query.startswith(name) or 
                    query.query.split()[0] == name 
                    for name in names):
                    await handler(query)

        @self.router.inline_query()
        async def handle_inline_query(query: InlineQuery):
            for handler in self.inline_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta or handler_meta.get("type") == "inline":
                    await handler(query)

        @self.router.callback_query()
        async def handle_callback_query(query: CallbackQuery):
            for handler in self.cbq_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta or handler_meta.get("type") == "callback_query":
                    await handler(query)
