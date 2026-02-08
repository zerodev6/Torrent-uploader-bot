from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
import json

@Client.on_message(filters.command("metadata") & filters.private)
async def metadata_menu(client, message):
    """Show metadata menu"""
    user_id = message.from_user.id
    
    # Check if user has access
    from plugins.start import check_force_sub
    if not await check_force_sub(client, message):
        return
    
    # Get user metadata
    user_data = await db.get_user(user_id)
    if not user_data:
        await db.add_user(user_id, message.from_user.first_name)
        user_data = await db.get_user(user_id)
    
    metadata = user_data.get("metadata", {})
    
    metadata_text = "<b>📝 Custom Metadata Settings</b>\n\n"
    
    if metadata:
        metadata_text += "<b>Current Metadata:</b>\n"
        for key, value in metadata.items():
            metadata_text += f"• <code>{key}</code>: <code>{value}</code>\n"
    else:
        metadata_text += "❌ No metadata set\n"
    
    metadata_text += "\n<b>How to use:</b>\n"
    metadata_text += "Send metadata in format:\n"
    metadata_text += "<code>key1:value1\nkey2:value2</code>\n\n"
    metadata_text += "<b>Example:</b>\n"
    metadata_text += "<code>title:My Video\nartist:John Doe\nalbum:Best Songs</code>"
    
    buttons = [
        [InlineKeyboardButton("➕ Add Metadata", callback_data="add_metadata_prompt")],
        [InlineKeyboardButton("🗑️ Clear All Metadata", callback_data="clear_metadata")],
        [InlineKeyboardButton("🔙 Close", callback_data="close_data")]
    ]
    
    await message.reply_text(
        metadata_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^add_metadata_prompt$"))
async def add_metadata_prompt(client, callback_query):
    """Prompt user to add metadata"""
    await callback_query.message.edit_text(
        "<b>📝 Add Custom Metadata</b>\n\n"
        "Send metadata in this format:\n"
        "<code>key1:value1\nkey2:value2</code>\n\n"
        "<b>Common metadata keys:</b>\n"
        "• title - Video/Audio title\n"
        "• artist - Artist name\n"
        "• album - Album name\n"
        "• year - Year\n"
        "• genre - Genre\n"
        "• comment - Comment\n\n"
        "<b>Example:</b>\n"
        "<code>title:My Awesome Video\nartist:John Doe\nyear:2024</code>\n\n"
        "Send your metadata now:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="back_to_metadata")]
        ])
    )
    
    # Set user state to waiting for metadata
    await db.update_user({
        "id": callback_query.from_user.id,
        "awaiting_metadata": True
    })

@Client.on_message(filters.text & filters.private)
async def receive_metadata(client, message):
    """Receive and save metadata"""
    user_id = message.from_user.id
    
    user_data = await db.get_user(user_id)
    if not user_data or not user_data.get("awaiting_metadata"):
        return
    
    # Parse metadata
    try:
        metadata = {}
        lines = message.text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        if not metadata:
            await message.reply_text(
                "❌ <b>Invalid format!</b>\n\n"
                "Please use format:\n"
                "<code>key:value</code>"
            )
            return
        
        # Save metadata
        await db.update_user({
            "id": user_id,
            "metadata": metadata,
            "awaiting_metadata": False
        })
        
        # Show saved metadata
        metadata_text = "✅ <b>Metadata saved successfully!</b>\n\n<b>Saved metadata:</b>\n"
        for key, value in metadata.items():
            metadata_text += f"• <code>{key}</code>: <code>{value}</code>\n"
        
        metadata_text += "\n<i>This metadata will be applied to your uploaded files.</i>"
        
        await message.reply_text(
            metadata_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 View Metadata", callback_data="back_to_metadata")]
            ])
        )
    
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Error parsing metadata:</b>\n<code>{str(e)}</code>\n\n"
            "Please check your format and try again."
        )

@Client.on_callback_query(filters.regex("^clear_metadata$"))
async def clear_metadata(client, callback_query):
    """Clear all metadata"""
    user_id = callback_query.from_user.id
    
    await db.update_user({
        "id": user_id,
        "metadata": {},
        "awaiting_metadata": False
    })
    
    await callback_query.answer("✅ All metadata cleared!", show_alert=True)
    await refresh_metadata_menu(client, callback_query.message, user_id)

@Client.on_callback_query(filters.regex("^back_to_metadata$"))
async def back_to_metadata(client, callback_query):
    """Go back to metadata menu"""
    await db.update_user({
        "id": callback_query.from_user.id,
        "awaiting_metadata": False
    })
    await refresh_metadata_menu(client, callback_query.message, callback_query.from_user.id)

async def refresh_metadata_menu(client, message, user_id):
    """Refresh metadata menu"""
    user_data = await db.get_user(user_id)
    metadata = user_data.get("metadata", {})
    
    metadata_text = "<b>📝 Custom Metadata Settings</b>\n\n"
    
    if metadata:
        metadata_text += "<b>Current Metadata:</b>\n"
        for key, value in metadata.items():
            metadata_text += f"• <code>{key}</code>: <code>{value}</code>\n"
    else:
        metadata_text += "❌ No metadata set\n"
    
    metadata_text += "\n<b>How to use:</b>\n"
    metadata_text += "Send metadata in format:\n"
    metadata_text += "<code>key1:value1\nkey2:value2</code>\n\n"
    metadata_text += "<b>Example:</b>\n"
    metadata_text += "<code>title:My Video\nartist:John Doe\nalbum:Best Songs</code>"
    
    buttons = [
        [InlineKeyboardButton("➕ Add Metadata", callback_data="add_metadata_prompt")],
        [InlineKeyboardButton("🗑️ Clear All Metadata", callback_data="clear_metadata")],
        [InlineKeyboardButton("🔙 Close", callback_data="close_data")]
    ]
    
    try:
        await message.edit_text(
            metadata_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        await message.reply_text(
            metadata_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
