from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from functools import wraps
from pydantic import BaseModel
from hashlib import sha256
import hmac
from typing import Callable

from tensai import db

class TelegramValidator:
    def __init__(self, token: str):
        self.token = token

    def __call__(self, func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            body = await request.json()
            init_data = body.get("initData")
            if not init_data:
                raise HTTPException(status_code=400, detail="Missing initData")

            data = self._transform_init_data(init_data)
            if not self._validate(data):
                raise HTTPException(status_code=403, detail="Invalid hash")
            return await func(request, *args, **kwargs)

        return wrapper

    def _transform_init_data(self, init_data: str) -> dict:
        return dict([kv.split("=", 1) for kv in init_data.split("&")])

    def _validate(self, data: dict) -> bool:
        check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"
        )

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=self.token.encode(),
            digestmod=sha256
        ).digest()

        computed_hash = hmac.new(
            key=secret_key,
            msg=check_string.encode(),
            digestmod=sha256
        ).hexdigest()

        return computed_hash == data.get("hash")

class UserResponse(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    username: str

class SettingsResponse(BaseModel):
    prefix: str
    lang: str

class InitializedResponse(BaseModel):
    initialized: bool

class UserRouter:
    def __init__(self, validator: TelegramValidator):
        self.router = APIRouter()
        self.validator = validator
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/me")
        #@self.validator
        async def get_user(request: Request) -> UserResponse:
            user = db.get("tensai.user", {})
            return UserResponse(**user)
        
        @self.router.get("/status")
        #@self.validator
        async def get_status(request: Request) -> InitializedResponse:
            token = db.get("tensai.bot.token", False)
            return InitializedResponse(initialized=bool(token))

class SettingsRouter:
    def __init__(self, validator: TelegramValidator):
        self.router = APIRouter()
        self.validator = validator
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/")
        #@self.validator
        async def get_settings(request: Request) -> SettingsResponse:
            settings = db.get("tensai.settings", {})
            return SettingsResponse(prefix=settings.get("prefix", "."), lang=settings.get("lang", "en"))

        @self.router.post("/prefix")
        #@self.validator
        async def set_prefix(request: Request):
            data = await request.json()
            prefix = data.get("prefix", ".")
            settings = db.get("tensai.settings", {})
            settings["prefix"] = prefix
            db.set("tensai.settings", settings)
            return JSONResponse({"ok": True, "prefix": prefix})

        @self.router.post("/lang")
        #@self.validator
        async def set_lang(request: Request):
            data = await request.json()
            lang = data.get("lang", "en")
            settings = db.get("tensai.settings", {})
            settings["lang"] = lang
            db.set("tensai.settings", settings)
            return JSONResponse({"ok": True, "lang": lang})

bot_token = db.get("tensai.bot.token")
validator = TelegramValidator(bot_token)

user_router = UserRouter(validator)
settings_router = SettingsRouter(validator)
