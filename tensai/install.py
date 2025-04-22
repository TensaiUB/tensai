from tensai import db, dp, bot
from aiogram import Router, types

router: Router = Router()

async def install_user() -> None:
    """Install the user."""

    print("Installing Tensai user...")
    me: any = await bot.get_me()
    
    print("Waiting for connection bot to Telegram Business...")
    print(f"Open Settings → Telegram Business → ChatBots → Add Bot @{me.username}")

    router.business_connection()(connect)
    dp.include_router(router)

async def connect(connection: types.BusinessConnection) -> None:
    """Connect telegram accouunt."""

    user: types.User = connection.user
    user_id: int = user.id

    db.set('tensai.user', {
        "telegram_id": user_id,
        "first_name": connection.user.first_name,
        "last_name": connection.user.last_name,
        "username": connection.user.username,
    })

    print("Telegram account connected.")

    rights: types.BusinessBotRights = connection.rights

    print("Rights:")
    for right, value in dict(rights).items():
        db.set(f'tensai.rights', {right: bool(value)})
        print(f"{right}: {value}")

    print("About rights: https://docs.aiogram.dev/en/latest/api/types/business_bot_rights.html")
