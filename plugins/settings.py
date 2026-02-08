from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db
import pytz
import os

# Available timezones
TIMEZONES = {
    "Asia/Kolkata": "🇮🇳 India (IST)",
    "America/New_York": "🇺🇸 USA East (EST)",
    "America/Los_Angeles": "🇺🇸 USA West (PST)",
    "Europe/London": "🇬🇧 UK (GMT)",
    "Asia/Dubai": "🇦🇪 UAE (GST)",
    "Asia/Tokyo": "🇯🇵 Japan (JST)",
    "Australia/Sydney": "🇦🇺 Australia (AEDT)",
}

@Client.on_message(filters.command("settings") & filters.private)
async def settings_menu(client, message):
    """Show settings menu"""
    user_id = message.from_user.id
    
    # Check if user has access
    from plugins.start import check_force_sub
    if not await check_force_sub(client, message):
        return
    
    # Get user settings
    user_data = await db.get_user(user_id)
    if not user_data:
        await db.add_user(user_id, message.from_user.first_name)
        user_data = await db.get_user(user_id)
    
    # Get current settings
    timezone = user_data.get("timezone", "Asia/Kolkata")
    spoiler = "ON" if user_data.get("spoiler_effect", False) else "OFF"
    show_rename = "ON" if user_data.get("show_rename", True) else "OFF"
    upload_as_doc = "ON" if user_data.get("upload_as_doc", True) else "OFF"
    receive_screenshots = "ON" if user_data.get("receive_screenshots", True) else "OFF"
    bot_updates = "ON" if user_data.get("bot_updates", True) else "OFF"
    has_thumbnail = "✅" if user_data.get("thumbnail") and os.path.exists(user_data.get("thumbnail")) else "❌"
    
    settings_text = f"""<b>⚙️ Bot Settings</b>

<b>Current Settings:</b>
⏰ Timezone: <code>{TIMEZONES.get(timezone, timezone)}</code>
🖼️ Thumbnail: {has_thumbnail}
🎆 Spoiler Effect: <code>{spoiler}</code>
✏️ Show Rename Option: <code>{show_rename}</code>
📥 Upload as Document: <code>{upload_as_doc}</code>
📷 Receive Screenshots: <code>{receive_screenshots}</code>
🤖 Receive Bot Updates: <code>{bot_updates}</code>

<b>Click buttons below to change settings:</b>"""
    
    buttons = [
        [InlineKeyboardButton("⏰ Set Timezone", callback_data="setting_timezone")],
        [InlineKeyboardButton("🖼️ See Thumbnail", callback_data="setting_view_thumb")],
        [InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="setting_delete_thumb")],
        [InlineKeyboardButton(f"🎆 Spoiler Effect: {spoiler}", callback_data="setting_toggle_spoiler")],
        [InlineKeyboardButton(f"✏️ Show Rename: {show_rename}", callback_data="setting_toggle_rename")],
        [InlineKeyboardButton(f"📥 Upload as Doc: {upload_as_doc}", callback_data="setting_toggle_doc")],
        [InlineKeyboardButton(f"📷 Receive Screenshots: {receive_screenshots}", callback_data="setting_toggle_screenshots")],
        [InlineKeyboardButton(f"🤖 Bot Updates: {bot_updates}", callback_data="setting_toggle_updates")],
        [InlineKeyboardButton("🔙 Close", callback_data="close_data")]
    ]
    
    await message.reply_text(
        settings_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^setting_"))
async def settings_callback(client, callback_query: CallbackQuery):
    """Handle settings callbacks"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    user_data = await db.get_user(user_id)
    if not user_data:
        await db.add_user(user_id, callback_query.from_user.first_name)
        user_data = await db.get_user(user_id)
    
    # Timezone selection
    if data == "setting_timezone":
        buttons = []
        for tz_key, tz_name in TIMEZONES.items():
            buttons.append([InlineKeyboardButton(tz_name, callback_data=f"settz_{tz_key}")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")])
        
        await callback_query.message.edit_text(
            "<b>⏰ Select Your Timezone</b>\n\n"
            "Choose your local timezone from the options below:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    # View thumbnail
    elif data == "setting_view_thumb":
        thumb_path = user_data.get("thumbnail")
        if thumb_path and os.path.exists(thumb_path):
            await callback_query.message.reply_photo(
                photo=thumb_path,
                caption="📸 <b>Your Current Thumbnail</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🗑️ Delete", callback_data="setting_delete_thumb")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]
                ])
            )
            await callback_query.answer()
        else:
            await callback_query.answer("❌ No thumbnail found! Use /addthum to add one.", show_alert=True)
    
    # Delete thumbnail
    elif data == "setting_delete_thumb":
        thumb_path = user_data.get("thumbnail")
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
            await db.update_user({"id": user_id, "thumbnail": None})
            await callback_query.answer("✅ Thumbnail deleted!", show_alert=True)
            await refresh_settings(client, callback_query.message, user_id)
        else:
            await callback_query.answer("❌ No thumbnail to delete!", show_alert=True)
    
    # Toggle spoiler effect
    elif data == "setting_toggle_spoiler":
        current = user_data.get("spoiler_effect", False)
        await db.update_user({"id": user_id, "spoiler_effect": not current})
        await callback_query.answer(f"🎆 Spoiler effect {'enabled' if not current else 'disabled'}!")
        await refresh_settings(client, callback_query.message, user_id)
    
    # Toggle rename option
    elif data == "setting_toggle_rename":
        current = user_data.get("show_rename", True)
        await db.update_user({"id": user_id, "show_rename": not current})
        await callback_query.answer(f"✏️ Rename option {'enabled' if not current else 'disabled'}!")
        await refresh_settings(client, callback_query.message, user_id)
    
    # Toggle upload as document
    elif data == "setting_toggle_doc":
        current = user_data.get("upload_as_doc", True)
        await db.update_user({"id": user_id, "upload_as_doc": not current})
        await callback_query.answer(f"📥 Upload as document {'enabled' if not current else 'disabled'}!")
        await refresh_settings(client, callback_query.message, user_id)
    
    # Toggle receive screenshots
    elif data == "setting_toggle_screenshots":
        current = user_data.get("receive_screenshots", True)
        await db.update_user({"id": user_id, "receive_screenshots": not current})
        await callback_query.answer(f"📷 Receive screenshots {'enabled' if not current else 'disabled'}!")
        await refresh_settings(client, callback_query.message, user_id)
    
    # Toggle bot updates
    elif data == "setting_toggle_updates":
        current = user_data.get("bot_updates", True)
        await db.update_user({"id": user_id, "bot_updates": not current})
        await callback_query.answer(f"🤖 Bot updates {'enabled' if not current else 'disabled'}!")
        await refresh_settings(client, callback_query.message, user_id)

@Client.on_callback_query(filters.regex("^settz_"))
async def set_timezone(client, callback_query: CallbackQuery):
    """Set user timezone"""
    user_id = callback_query.from_user.id
    timezone = callback_query.data.replace("settz_", "")
    
    await db.update_user({"id": user_id, "timezone": timezone})
    await callback_query.answer(f"✅ Timezone set to {TIMEZONES.get(timezone, timezone)}!")
    await refresh_settings(client, callback_query.message, user_id)

@Client.on_callback_query(filters.regex("^back_to_settings$"))
async def back_to_settings(client, callback_query: CallbackQuery):
    """Go back to settings menu"""
    await refresh_settings(client, callback_query.message, callback_query.from_user.id)

async def refresh_settings(client, message, user_id):
    """Refresh settings menu"""
    user_data = await db.get_user(user_id)
    
    timezone = user_data.get("timezone", "Asia/Kolkata")
    spoiler = "ON" if user_data.get("spoiler_effect", False) else "OFF"
    show_rename = "ON" if user_data.get("show_rename", True) else "OFF"
    upload_as_doc = "ON" if user_data.get("upload_as_doc", True) else "OFF"
    receive_screenshots = "ON" if user_data.get("receive_screenshots", True) else "OFF"
    bot_updates = "ON" if user_data.get("bot_updates", True) else "OFF"
    has_thumbnail = "✅" if user_data.get("thumbnail") and os.path.exists(user_data.get("thumbnail")) else "❌"
    
    settings_text = f"""<b>⚙️ Bot Settings</b>

<b>Current Settings:</b>
⏰ Timezone: <code>{TIMEZONES.get(timezone, timezone)}</code>
🖼️ Thumbnail: {has_thumbnail}
🎆 Spoiler Effect: <code>{spoiler}</code>
✏️ Show Rename Option: <code>{show_rename}</code>
📥 Upload as Document: <code>{upload_as_doc}</code>
📷 Receive Screenshots: <code>{receive_screenshots}</code>
🤖 Receive Bot Updates: <code>{bot_updates}</code>

<b>Click buttons below to change settings:</b>"""
    
    buttons = [
        [InlineKeyboardButton("⏰ Set Timezone", callback_data="setting_timezone")],
        [InlineKeyboardButton("🖼️ See Thumbnail", callback_data="setting_view_thumb")],
        [InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="setting_delete_thumb")],
        [InlineKeyboardButton(f"🎆 Spoiler Effect: {spoiler}", callback_data="setting_toggle_spoiler")],
        [InlineKeyboardButton(f"✏️ Show Rename: {show_rename}", callback_data="setting_toggle_rename")],
        [InlineKeyboardButton(f"📥 Upload as Doc: {upload_as_doc}", callback_data="setting_toggle_doc")],
        [InlineKeyboardButton(f"📷 Receive Screenshots: {receive_screenshots}", callback_data="setting_toggle_screenshots")],
        [InlineKeyboardButton(f"🤖 Bot Updates: {bot_updates}", callback_data="setting_toggle_updates")],
        [InlineKeyboardButton("🔙 Close", callback_data="close_data")]
    ]
    
    try:
        await message.edit_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        await message.reply_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
