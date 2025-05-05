from aiogram.types import Message, InlineQuery, CallbackQuery
from tensai import db, utils
from aiogram import F


class Decorators:
    def command(self, aliases=None, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "command",
                "aliases": aliases or [],
                "description": description or {},
                "only_me": only_me or False
            }
            return func
        return decorator

    def bot_command(self, aliases=None, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "bot_command",
                "aliases": aliases or [],
                "description": description or {},
                "only_me": only_me or False
            }
            return func
        return decorator

    def inline_command(self, aliases=None, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "inline_command",
                "aliases": aliases or [],
                "description": description or {},
                "only_me": only_me or False
            }
            return func
        return decorator

    def inline(self, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "inline",
                "description": description or {},
                "only_me": only_me or False
            }
            return func
        return decorator

    def bot_message(self, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "bot_message",
                "description": description or {},
                "only_me": only_me or False
            }
            return func
        return decorator

    def callback_query(self, data=None, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "callback_query",
                "data": data or None,
                "description": description or {},
                "only_me": only_me or None
            }
            return func
        return decorator

    def business_message(self, description=None, only_me=True):
        def decorator(func):
            func._handler_meta = {
                "type": "business_message",
                "description": description or {},
                "only_me": only_me or False
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

            from_user_id = message.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.cmd_handlers:
                if not getattr(message, "text", ""):
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                    only_me = handler_meta['only_me']
                else:
                    names = [handler.__name__.replace("_cmd_", "")]
                    only_me = True

                if (only_me
                    and from_user_id != user_id
                    and from_user_id not in owners    
                ):
                    continue

                if (
                    any(
                        message.text == f"{prefix}{name}" or message.text.startswith(f"{prefix}{name} ")
                        for name in names
                    )
                or any(
                    message.text == f"{prefix} {name}" or message.text.startswith(f"{prefix} {name} ")
                    for name in names
                )):
                    await handler(message)

            for handler in self.bismsg_handlers:
                await handler(message)

        @self.router.message(F.text.startswith("/"))
        async def handle_bot_message(message: Message):
            from_user_id = message.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.botcmd_handlers:
                if not getattr(message, "text", ""):
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                    only_me = handler['only_me']
                else:
                    names = [handler.__name__.replace("_botcmd_", "")]
                    only_me = True
                
                if (only_me
                    and from_user_id == user_id 
                    or from_user_id in owners
                ):
                    continue

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
            from_user_id = message.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.botmsg_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta:
                    await handler(message)
                if handler_meta:
                    only_me = handler_meta['only_me']
                    if (only_me
                        and from_user_id == user_id 
                        or from_user_id in owners
                    ):
                        continue

        @self.router.inline_query(F.query)
        async def handle_inlinecmd_query(query: InlineQuery):
            from_user_id = query.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])
            
            for handler in self.inlinecmd_handlers:
                if not query.query:
                    continue

                handler_meta = getattr(handler, "_handler_meta", {})

                if handler_meta:
                    names = [handler.__name__]
                    names.extend(handler_meta.get("aliases", []))
                    only_me = handler['only_me']
                else:
                    names = [handler.__name__.replace("_inlinecmd_", "")]
                    only_me = True

                if (only_me
                    and from_user_id == user_id 
                    or from_user_id in owners
                ):
                    continue

                if any(query.query.startswith(name) or 
                    query.query.split()[0] == name 
                    for name in names):
                    await handler(query)

        @self.router.inline_query()
        async def handle_inline_query(inline_query: InlineQuery):
            from_user_id = inline_query.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.inline_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta:
                    await handler(inline_query)
                if handler_meta:
                    only_me = handler_meta['only_me']
                    if (only_me
                        and from_user_id != user_id
                        and from_user_id not in owners
                    ):
                        continue
                    return await handler(inline_query)

        @self.router.callback_query()
        async def handle_callback_query(callback: CallbackQuery):
            from_user_id = callback.from_user.id
            user_id = db.get("tensai.user.telegram_id")
            owners = db.get("tensai.security.owners", [])

            for handler in self.cbq_handlers:
                handler_meta = getattr(handler, "_handler_meta", {})
                if not handler_meta:
                    await handler(callback)
                if handler_meta:
                    if handler_meta.get("data", "") == callback.data:
                        only_me = handler_meta['only_me']
                        if (only_me
                            and from_user_id != user_id
                            and from_user_id not in owners
                        ):
                            continue
                        return await handler(callback)