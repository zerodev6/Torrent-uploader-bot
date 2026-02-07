import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Script import script
from config import config
from database.users_chats_db import db
import requests

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # Add user to database
    await db.add_user(user_id, name)
    
    # Check force subscribe
    if not await check_force_sub(client, message):
        return
    
    # Send ⏳ emoji animation
    loading_msg = await message.reply("⏳")
    await asyncio.sleep(2)
    await loading_msg.delete()
    
    # Get random welcome image
    try:
        response = requests.get(config.WELCOME_IMAGE_API)
        if response.status_code == 200:
            image_url = response.url
        else:
            image_url = "https://graph.org/file/86da2027469565b5873d6.jpg"
    except:
        image_url = "https://graph.org/file/86da2027469565b5873d6.jpg"
    
    # Welcome buttons
    buttons = [
        [
            InlineKeyboardButton("✨ Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("💎 Premium", callback_data="premium_info")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{config.OWNER_USERNAME.replace('@', '')}")
        ]
    ]
    
    await message.reply_photo(
        photo=image_url,
        caption=script.START_TXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("start") & filters.group)
async def group_start(client, message):
    chat_id = message.chat.id
    title = message.chat.title
    
    # Add group to database
    await db.add_chat(chat_id, title)
    
    buttons = [
        [
            InlineKeyboardButton("✨ Help", callback_data="help"),
            InlineKeyboardButton("💎 Premium", callback_data="premium_info")
        ]
    ]
    
    await message.reply_text(
        script.GSTART_TXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def check_force_sub(client, message):
    """Check if user has joined all force subscribe channels"""
    user_id = message.from_user.id
    
    # Admin bypass
    if user_id in config.ADMINS or user_id == config.OWNER_ID:
        return True
    
    not_joined = []
    
    for channel in config.FORCE_SUB_CHANNELS:
        try:
            channel_username = channel.replace("https://t.me/", "").replace("@", "")
            member = await client.get_chat_member(f"@{channel_username}", user_id)
            if member.status in ["kicked", "left"]:
                not_joined.append(f"@{channel_username}")
        except Exception as e:
            not_joined.append(f"@{channel_username}")
    
    if not_joined:
        channels_text = "\n".join([f"📢 {ch}" for ch in not_joined])
        buttons = [
            [InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.replace('@', '')}")]
            for ch in not_joined
        ]
        buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_sub")])
        
        await message.reply_photo(
            photo=config.FORCE_SUB_IMAGE,
            caption=script.FORCE_SUB_TEXT.format(channels=channels_text),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return False
    
    return True

@Client.on_callback_query(filters.regex("^check_sub$"))
async def check_sub_callback(client, callback_query):
    """Recheck force subscribe"""
    if await check_force_sub(client, callback_query.message):
        await callback_query.message.delete()
        await callback_query.message.reply("✅ Access granted! You can now use the bot.")
    else:
        await callback_query.answer("❌ Please join all channels first!", show_alert=True)

@Client.on_callback_query(filters.regex("^(help|about)$"))
async def info_callbacks(client, callback_query):
    """Handle help and about callbacks"""
    query = callback_query.data
    
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="start")]]
    
    if query == "help":
        await callback_query.message.edit_text(
            script.HELP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif query == "about":
        bot = await client.get_me()
        await callback_query.message.edit_text(
            script.ABOUT_TXT.format(bot.username, bot.first_name),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client, callback_query):
    """Back to start"""
    buttons = [
        [
            InlineKeyboardButton("✨ Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("💎 Premium", callback_data="premium_info")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{config.OWNER_USERNAME.replace('@', '')}")
        ]
    ]
    
    await callback_query.message.edit_text(
        script.START_TXT.format(callback_query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^close_data$"))
async def close_callback(client, callback_query):
    """Close message"""
    await callback_query.message.delete()
