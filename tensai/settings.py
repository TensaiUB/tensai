from fakeredis import aioredis as fake_aioredis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError
from rich import print

import logging


logger = logging.getLogger(__name__)

async def get_redis():
    try:
        redis_client = Redis(
            host="localhost", port=6379, password=None, decode_responses=True
        )
        await redis_client.ping()
        print("[green]✅ Connected to Redis[/green]")
        logger.info("Connected to Redis")
        return redis_client
    except (ConnectionError, RedisError, OSError):
        print("[green]✅ Connected to fake Redis[/green]")
        logger.info("Connected to fake Redis")
        return await fake_aioredis.FakeRedis(decode_responses=True)


def get_web_settings(db, sys_args):
    if "--use-web" in sys_args:
        web = True
    elif "--no-web" in sys_args:
        web = False
    else:
        if not db.get("tensai.settings.web"):
            web_input = (
                input("\nDo you want to use web as default? (y/n): ").strip().lower()
            )
            web = web_input == "y"
        else:
            web = db.get("tensai.settings.web.use_web")

    port = db.get("tensai.settings.web.port", 8080)

    if web:
        import argparse

        parser = argparse.ArgumentParser(description="Get args")
        parser.add_argument("--port", type=str, help="Port", required=False)
        args, unknown = parser.parse_known_args()

        if args.port:
            port = args.port
        else:
            if not db.get("tensai.settings.web"):
                port_input = input(
                    "What port do you want to use? (Press enter to use default 8080): "
                ).strip()
                if port_input:
                    port = int(port_input)

    db.set("tensai.settings.web", {"use_web": web, "port": port})

    return web, port
