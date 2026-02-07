import os
import asyncio
import logging
from pyrogram import Client
from config import config

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

if __name__ == "__main__":
    bot = Bot()
    bot.run()
