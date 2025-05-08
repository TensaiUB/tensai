# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tensai import db
import uvicorn
import asyncio
from fastapi.staticfiles import StaticFiles

from tensai.web.api import user_router, settings_router

app = FastAPI()
installer_done = asyncio.Event()

BUILD_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=BUILD_DIR / "static"), name="static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_file = BUILD_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return {"error": "index.html not found"}

@app.post("/submit")
async def submit_token(token: str = Form(...)):
    try:
        bot = Bot(token=token)
        await bot.get_me()
        db.set("tensai.bot.token", token)

        installer_done.set()

        return {
            "status": "success",
            "message": "Token is valid. Bot installed successfully.",
            "bot_info": {
                "username": bot.username,
                "first_name": bot.first_name,
                "last_name": bot.last_name,
                "id": bot.id
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def start_webinstaller() -> str:
    port = db.get("tensai.settings.web.port", 8080)
    
    config = uvicorn.Config("tensai.web.web_installer:app", host="0.0.0.0", port=port, log_level="error", loop="asyncio")
    server = uvicorn.Server(config)

    print(f"\n✅ Log in via web: http://127.0.0.1:{port}")

    async def server_task():
        await server.serve()

    server_task_future = asyncio.create_task(server_task())

    await installer_done.wait()

    server_task_future.cancel()

    return db.get("tensai.bot.token")

app.include_router(user_router.router, tags=["user"], prefix="/api")
app.include_router(settings_router.router, tags=["settings"], prefix="/api")
