# This file is part of Tensai userbot.
# the telegram userbot.
#
# © 2025 @fajox & @vsecoder
#
# For license and copyright information please follow this link:
# https://github.com/tensaiub/tensai/blob/master/LICENSE

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tensai import db
import uvicorn
import asyncio

app = FastAPI()
installer_done = asyncio.Event()

@app.get("/", response_class=HTMLResponse)
async def installer_page():
    with open("tensai/web/static/login.html", "r", encoding="utf-8") as file:
        return file.read()

@app.post("/submit")
async def submit_token(token: str = Form(...)):
    try:
        bot = Bot(
            token=token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            )
        )
        db.set("tensai.bot.token", token)

        with open("tensai/web/static/success.html", "r", encoding="utf-8") as file:
            sucess_page = file.read()

        installer_done.set()

        return HTMLResponse(
            content=sucess_page,
            status_code=200
        )
    
    except Exception as e:        
        with open("tensai/web/static/error.html", "r", encoding="utf-8") as file:
            error_page = file.read()
        return HTMLResponse(
            content=error_page,
            status_code=400
        )

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