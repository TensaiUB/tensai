from tensai import db, dp, bot
from aiogram import Router, types
from rich import print

router = Router()

async def install_user() -> None:
    """Install the user and register connection handler."""

    print("Installing Tensai user...")
    me = await bot.get_me()

    if not db.get("tensai.user"):
        print("[sky_blue1]Waiting for bot connection to Telegram Business...[/sky_blue1]")
        print(f"[sky_blue1]Open Settings → Telegram Business → ChatBots → Add Bot @{me.username}[/sky_blue1]")
    else:
        print("[sky_blue1]Telegram account connected.[/sky_blue1]")

    router.business_connection()(connect)
    dp.include_router(router)

async def connect(connection: types.BusinessConnection) -> None:
    """Handle Telegram Business connection."""

    user = connection.user
    user_id = user.id

    owner_id = db.get("tensai.user.telegram_id")

    if owner_id and owner_id != user_id:
        await bot.send_message(user_id, "<b>❌ You are not the owner of this bot.</b>")
        return

    message = (
        "<b>✅ Your account has been successfully connected to Tensai.</b>"
        if not db.get("tensai.user")
        else "<b>✅ Rights of the bot have been successfully updated!</b>"
    )
    await bot.send_message(user_id, message)
    print("[sky_blue1]Telegram account connected.[/sky_blue1]" if not db.get("tensai.user") else "[sky_blue1]Rights successfully updated.[/sky_blue1]")

    db.set('tensai.user', {
        "telegram_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    })

    rights_dict = {key: bool(value) for key, value in dict(connection.rights).items()}
    db.set('tensai.rights', rights_dict)