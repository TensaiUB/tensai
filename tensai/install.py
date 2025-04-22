from tensai import db, dp, bot
from aiogram import Router, types

from rich import print

router: Router = Router()

async def install_user() -> None:
    """Install the user."""

    print("Installing Tensai user...")
    me: any = await bot.get_me()
    
    print("[sky_blue1]Waiting for connection bot to Telegram Business...[/sky_blue1]")
    print(f"[sky_blue1]Open Settings → Telegram Business → ChatBots → Add Bot @{me.username}[/sky_blue1]")

    router.business_connection()(connect)
    dp.include_router(router)

async def connect(connection: types.BusinessConnection) -> None:
    """Connect telegram accouunt."""

    user: types.User = connection.user
    user_id: int = user.id

    owner = db.get("tensai.user.telegram_id", None)

    if owner != user_id and owner:
        return await bot.send_message(user_id, "<b>You are not the owner of this bot.</b>")

    db.set('tensai.user', {
        "telegram_id": user_id,
        "first_name": connection.user.first_name,
        "last_name": connection.user.last_name,
        "username": connection.user.username,
    })

    print("[sky_blue1]Telegram account connected.[/sky_blue1]")

    rights: types.BusinessBotRights = connection.rights

    # print("Rights:")
    for right, value in dict(rights).items():
        db.set('tensai.rights', {right: value})
        # print(f"{right}: {value}")

    # print("About rights: https://docs.aiogram.dev/en/latest/api/types/business_bot_rights.html")

    await bot.send_message(user_id, "<b>✅ Your account has been successfully connected to Tensai.</b>")