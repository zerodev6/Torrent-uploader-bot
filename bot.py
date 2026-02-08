import os
import asyncio
import logging
from pyrogram import Client
from config import config
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Create downloads directory
os.makedirs(config.DOWNLOAD_LOCATION, exist_ok=True)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="TorrentBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins={"root": "plugins"}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"Bot started as @{me.username}")
        config.BOT_USERNAME = me.username
        
    async def stop(self):
        await super().stop()
        logging.info("Bot stopped!")

# Web server handlers
async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    
    # Get port from environment variable, default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    bot = Bot()
    
    # Start web server
    await start_web_server()
    
    # Start bot
    await bot.start()
    
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
