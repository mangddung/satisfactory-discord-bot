import asyncio
from .satisfactory_api import get_server_status
from .embed import update_server_embed
from config import SERVER_CHECK_INTERVAL
from db import *

async def periodic_server_check(bot):
    await bot.wait_until_ready()
    while True: 
        print("start server check")
        db = get_session()
        server_settings = db.query(ServerSettings).all()
        for server in server_settings:
            base_url = f"https://{server.server_ip}:{server.server_port}/api/v1"
            try:
                data = await asyncio.to_thread(get_server_status, base_url, server.api_token, 5)
                if not data:
                    data = {}
                await update_server_embed(db, bot, data, server)

            except Exception as ex:
                data = {}
                await update_server_embed(db, bot, data, server)
                continue
        
        db.close()
        await asyncio.sleep(SERVER_CHECK_INTERVAL)