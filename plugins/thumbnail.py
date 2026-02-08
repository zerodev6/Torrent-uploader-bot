from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database.users_chats_db import db
from config import config
import os

THUMB_LOCATION = "./thumbnails/"
os.makedirs(THUMB_LOCATION, exist_ok=True)

@Client.on_message(filters.command("addthum") & filters.private)
async def add_thumbnail(client, message):
    """Add thumbnail for user"""
    user_id = message.from_user.id
    
    # Check if user has access
    from plugins.start import check_force_sub
    if not await check_force_sub(client, message):
        return
    
    await message.reply_text(
        "📸 <b>Send me a photo to set as thumbnail</b>\n\n"
        "This thumbnail will be used for your videos and documents.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="close_data")]
        ])
    )

@Client.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message):
    """Save user's thumbnail"""
    user_id = message.from_user.id
    
    # Check if user settings allow receiving screenshots
    user_data = await db.get_user(user_id)
    if user_data and not user_data.get("receive_screenshots", True):
        return
    
    thumb_path = f"{THUMB_LOCATION}{user_id}.jpg"
    
    await message.download(file_name=thumb_path)
    
    # Save to database
    await db.update_user({
        "id": user_id,
        "thumbnail": thumb_path
    })
    
    await message.reply_text(
        "✅ <b>Thumbnail saved successfully!</b>\n\n"
        "Use /viewthum to view your thumbnail\n"
        "Use /delectthum to delete it",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👁️ View Thumbnail", callback_data="view_thumb")]
        ])
    )

@Client.on_message(filters.command("viewthum") & filters.private)
async def view_thumbnail(client, message):
    """View user's thumbnail"""
    user_id = message.from_user.id
    
    user_data = await db.get_user(user_id)
    thumb_path = user_data.get("thumbnail") if user_data else None
    
    if thumb_path and os.path.exists(thumb_path):
        await message.reply_photo(
            photo=thumb_path,
            caption="📸 <b>Your Current Thumbnail</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="delete_thumb")]
            ])
        )
    else:
        await message.reply_text(
            "❌ <b>No thumbnail found!</b>\n\n"
            "Use /addthum to add a thumbnail",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Thumbnail", callback_data="add_thumb_prompt")]
            ])
        )

@Client.on_message(filters.command("delectthum") & filters.private)
async def delete_thumbnail(client, message):
    """Delete user's thumbnail"""
    user_id = message.from_user.id
    
    user_data = await db.get_user(user_id)
    thumb_path = user_data.get("thumbnail") if user_data else None
    
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)
        
        # Update database
        await db.update_user({
            "id": user_id,
            "thumbnail": None
        })
        
        await message.reply_text("✅ <b>Thumbnail deleted successfully!</b>")
    else:
        await message.reply_text("❌ <b>No thumbnail to delete!</b>")

@Client.on_callback_query(filters.regex("^view_thumb$"))
async def view_thumb_callback(client, callback_query):
    """View thumbnail callback"""
    user_id = callback_query.from_user.id
    
    user_data = await db.get_user(user_id)
    thumb_path = user_data.get("thumbnail") if user_data else None
    
    if thumb_path and os.path.exists(thumb_path):
        await callback_query.message.reply_photo(
            photo=thumb_path,
            caption="📸 <b>Your Current Thumbnail</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="delete_thumb")]
            ])
        )
    else:
        await callback_query.answer("❌ No thumbnail found!", show_alert=True)

@Client.on_callback_query(filters.regex("^delete_thumb$"))
async def delete_thumb_callback(client, callback_query):
    """Delete thumbnail callback"""
    user_id = callback_query.from_user.id
    
    user_data = await db.get_user(user_id)
    thumb_path = user_data.get("thumbnail") if user_data else None
    
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)
        
        await db.update_user({
            "id": user_id,
            "thumbnail": None
        })
        
        await callback_query.message.edit_caption(
            "✅ <b>Thumbnail deleted successfully!</b>"
        )
    else:
        await callback_query.answer("❌ No thumbnail to delete!", show_alert=True)

@Client.on_callback_query(filters.regex("^add_thumb_prompt$"))
async def add_thumb_prompt_callback(client, callback_query):
    """Add thumbnail prompt callback"""
    await callback_query.message.edit_text(
        "📸 <b>Send me a photo to set as thumbnail</b>\n\n"
        "This thumbnail will be used for your videos and documents.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="close_data")]
        ])
    )
