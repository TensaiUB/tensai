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
from tensai import db
import uvicorn
import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from tensai.web.api import user_router, settings_router

app = FastAPI()
installer_done = asyncio.Event()

BUILD_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=BUILD_DIR / "static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router.router, tags=["user"], prefix="/api")
app.include_router(settings_router.router, tags=["settings"], prefix="/api")

@app.get("/")
async def serve_react_app():
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

async def start_web() -> None:
    port = db.get("tensai.settings.web.port", 8080)
    
    config = uvicorn.Config("tensai.web.web:app", host="0.0.0.0", port=port, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)

    print(f"\n✅ Log in via web: http://127.0.0.1:{port}")

    async def server_task():
        await server.serve()

    asyncio.create_task(server_task())
