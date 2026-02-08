import motor.motor_asyncio
from config import config
import datetime
import pytz

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.chats = self.db.chats

    # User Management
    async def add_user(self, user_id, name):
        user = await self.users.find_one({"id": user_id})
        if not user:
            return await self.users.insert_one({
                "id": user_id,
                "name": name,
                "joined_date": datetime.datetime.now(pytz.timezone("Asia/Kolkata")),
                "expiry_time": None,
                "downloads": 0,
                "total_data": 0,
                # New fields for settings
                "timezone": "Asia/Kolkata",
                "thumbnail": None,
                "spoiler_effect": False,
                "show_rename": True,
                "upload_as_doc": True,
                "receive_screenshots": True,
                "bot_updates": True,
                "metadata": {},
                "awaiting_metadata": False,
                "awaiting_rename": False
            })
        return False

    async def get_user(self, user_id):
        return await self.users.find_one({"id": user_id})

    async def get_all_users(self):
        return self.users.find({})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def update_user(self, user_data):
        await self.users.update_one(
            {"id": user_data["id"]},
            {"$set": user_data},
            upsert=True
        )

    async def delete_user(self, user_id):
        await self.users.delete_one({"id": user_id})

    async def is_premium_user(self, user_id):
        user = await self.get_user(user_id)
        if user and user.get("expiry_time"):
            expiry = user.get("expiry_time")
            if expiry.replace(tzinfo=pytz.UTC) > datetime.datetime.now(pytz.UTC):
                return True
            else:
                # Remove expired premium
                await self.remove_premium_access(user_id)
                return False
        return False

    async def remove_premium_access(self, user_id):
        user = await self.get_user(user_id)
        if user and user.get("expiry_time"):
            await self.users.update_one(
                {"id": user_id},
                {"$set": {"expiry_time": None}}
            )
            return True
        return False

    async def update_download_stats(self, user_id, file_size):
        await self.users.update_one(
            {"id": user_id},
            {
                "$inc": {
                    "downloads": 1,
                    "total_data": file_size
                }
            }
        )

    # Chat/Group Management
    async def add_chat(self, chat_id, title):
        chat = await self.chats.find_one({"id": chat_id})
        if not chat:
            return await self.chats.insert_one({
                "id": chat_id,
                "title": title,
                "joined_date": datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            })
        return False

    async def get_all_chats(self):
        return self.chats.find({})

    async def total_chat_count(self):
        return await self.chats.count_documents({})

    async def delete_chat(self, chat_id):
        await self.chats.delete_one({"id": chat_id})

db = Database(config.DATABASE_URI, config.DATABASE_NAME)
