# Compatibility layer for imports
from config import config

# Re-export config values for backward compatibility
ADMINS = config.ADMINS
OWNER_ID = config.OWNER_ID
DATABASE_URI = config.DATABASE_URI
BOT_TOKEN = config.BOT_TOKEN
API_ID = config.API_ID
API_HASH = config.API_HASH
FORCE_SUB_CHANNELS = config.FORCE_SUB_CHANNELS
PREMIUM_LOGS = config.PREMIUM_LOGS
SUBSCRIPTION = config.SUBSCRIPTION
STAR_PREMIUM_PLANS = config.STAR_PREMIUM_PLANS
