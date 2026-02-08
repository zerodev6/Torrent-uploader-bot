import os
from os import environ

class Config:
    # Bot Configuration
    API_ID = int(environ.get("API_ID", "0"))
    API_HASH = environ.get("API_HASH", "")
    BOT_TOKEN = environ.get("BOT_TOKEN", "")
    STRING_SESSION = environ.get("STRING_SESSION", "")
    
    # Database
    DATABASE_URI = environ.get("DATABASE_URI", "")
    DATABASE_NAME = environ.get("DATABASE_NAME", "torrent_bot")
    
    # Admin & Owner
    ADMINS = [int(admin) if admin.isdigit() else admin for admin in environ.get('ADMINS', '').split()]
    OWNER_ID = int(environ.get("OWNER_ID", "0"))
    OWNER_USERNAME = environ.get("OWNER_USERNAME", "@Venuboyy")
    
    # Force Subscribe Channels
    FORCE_SUB_CHANNELS = environ.get("FORCE_SUB_CHANNELS", "zerodev2,mvxyoffcail").split(",")
    FORCE_SUB_IMAGE = "https://i.ibb.co/pr2H8cwT/img-8312532076.jpg"
    
    # Welcome Image API
    WELCOME_IMAGE_API = "https://i.ibb.co/DgrswcPP/img-8108646188.jpg"
    
    # Download Limits (in bytes)
    FREE_LIMIT = int(environ.get("FREE_LIMIT", str(2 * 1024 * 1024 * 1024)))  # 2GB
    PREMIUM_LIMIT = int(environ.get("PREMIUM_LIMIT", str(4 * 1024 * 1024 * 1024)))  # 4GB
    
    # Download Path
    DOWNLOAD_LOCATION = environ.get("DOWNLOAD_LOCATION", "./downloads/")
    
    # Premium Logs
    PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", "0"))
    
    # Premium Plans with Stars
    STAR_PREMIUM_PLANS = {
        50: "7 days",
        100: "1 month",
        250: "3 months",
        500: "6 months",
        1000: "1 year"
    }
    
    # Bot Username
    BOT_USERNAME = environ.get("BOT_USERNAME", "")
    
    # Subscription Image
    SUBSCRIPTION = environ.get("SUBSCRIPTION", "https://graph.org/file/86da2027469565b5873d6.jpg")

config = Config()
