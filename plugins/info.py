import psutil
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Script import script
from config import config
from database.users_chats_db import db
from utils import humanbytes
import pytz
import datetime

# Bot start time
start_time = time.time()

@Client.on_message(filters.command("info"))
async def user_info(client, message):
    """Show user information"""
    user_id = message.from_user.id
    name = message.from_user.mention
    
    # Get user data
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await db.add_user(user_id, message.from_user.first_name)
        user_data = await db.get_user(user_id)
    
    downloads = user_data.get("downloads", 0)
    total_data = user_data.get("total_data", 0)
    joined_date = user_data.get("joined_date", datetime.datetime.now(pytz.timezone("Asia/Kolkata")))
    
    # Format joined date
    joined_str = joined_date.strftime("%d-%m-%Y")
    
    # Check premium status
    is_premium = await db.is_premium_user(user_id)
    
    if is_premium and user_data.get("expiry_time"):
        expiry = user_data.get("expiry_time")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str = expiry_ist.strftime("%d-%m-%Y %I:%M %p")
        
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_left_str = f"{days}d {hours}h {minutes}m"
        
        info_text = script.PREMIUM_USER_INFO.format(
            user_id=user_id,
            name=name,
            joined_date=joined_str,
            expiry_date=expiry_str,
            time_left=time_left_str,
            downloads=downloads,
            total_data=humanbytes(total_data)
        )
    else:
        info_text = script.USER_INFO.format(
            user_id=user_id,
            name=name,
            joined_date=joined_str,
            premium_status="❌ Not Active",
            downloads=downloads,
            total_data=humanbytes(total_data)
        )
    
    buttons = [[InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")]]
    
    await message.reply_text(
        info_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("status") & filters.user(config.ADMINS))
async def bot_status(client, message):
    """Show bot status (Admin only)"""
    
    # System stats
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Bot stats
    total_users = await db.total_users_count()
    total_groups = await db.total_chat_count()
    
    # Count premium users
    premium_count = 0
    users = await db.get_all_users()
    async for user in users:
        if await db.is_premium_user(user['id']):
            premium_count += 1
    
    # Uptime
    uptime_seconds = time.time() - start_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    
    status_text = f"""<b>📊 BOT STATUS</b>

<b>🤖 Bot Stats:</b>
👥 Total Users: <code>{total_users}</code>
👥 Premium Users: <code>{premium_count}</code>
💬 Total Groups: <code>{total_groups}</code>

<b>💻 System Stats:</b>
🔥 CPU Usage: <code>{cpu_usage}%</code>
🧠 RAM Usage: <code>{ram.percent}%</code>
💾 Disk Usage: <code>{disk.percent}%</code>

<b>📈 Storage:</b>
💾 Total: <code>{humanbytes(disk.total)}</code>
✅ Used: <code>{humanbytes(disk.used)}</code>
⚪️ Free: <code>{humanbytes(disk.free)}</code>

<b>⏰ Uptime:</b> <code>{uptime_str}</code>"""
    
    await message.reply_text(status_text)

@Client.on_message(filters.command("stats") & filters.user(config.ADMINS))
async def bot_stats(client, message):
    """Detailed bot statistics (Admin only)"""
    
    total_users = await db.total_users_count()
    total_groups = await db.total_chat_count()
    
    # Count premium users
    premium_count = 0
    total_downloads = 0
    total_data_downloaded = 0
    
    users = await db.get_all_users()
    async for user in users:
        user_data = await db.get_user(user['id'])
        if await db.is_premium_user(user['id']):
            premium_count += 1
        if user_data:
            total_downloads += user_data.get("downloads", 0)
            total_data_downloaded += user_data.get("total_data", 0)
    
    stats_text = f"""<b>📊 DETAILED STATISTICS</b>

<b>👥 User Statistics:</b>
• Total Users: <code>{total_users}</code>
• Premium Users: <code>{premium_count}</code>
• Free Users: <code>{total_users - premium_count}</code>

<b>💬 Group Statistics:</b>
• Total Groups: <code>{total_groups}</code>

<b>📥 Download Statistics:</b>
• Total Downloads: <code>{total_downloads}</code>
• Total Data: <code>{humanbytes(total_data_downloaded)}</code>
• Avg per User: <code>{humanbytes(total_data_downloaded // total_users) if total_users > 0 else '0 B'}</code>"""
    
    await message.reply_text(stats_text)
