import datetime
import time
import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.errors import FloodWait
from database import db
from config import Config
from utils import users_broadcast, groups_broadcast, temp, get_readable_time, clear_junk, junk_group
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ADMINS = Config.ADMINS
lock = asyncio.Lock()

# Store pending broadcast confirmations
pending_broadcasts = {}

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, target = query.data.split("#", 1)
    if target == 'users':
        temp.B_USERS_CANCEL = True
        await query.message.edit("🛑 ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜꜱᴇʀꜱ ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")
    elif target == 'groups':
        temp.B_GROUPS_CANCEL = True
        await query.message.edit("🛑 ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘꜱ ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")

@Client.on_callback_query(filters.regex(r'^pin_choice'))
async def handle_pin_choice(bot, query):
    """Handle pin Yes/No callback"""
    user_id = query.from_user.id
    
    if user_id not in pending_broadcasts:
        await query.answer("❌ Session expired. Please start broadcast again.", show_alert=True)
        return
    
    _, choice, broadcast_type = query.data.split("#")
    is_pin = choice == "yes"
    
    # Get stored data
    data = pending_broadcasts[user_id]
    b_msg = data['message']
    
    # Delete the question message
    await query.message.delete()
    
    # Start the appropriate broadcast
    if broadcast_type == "users":
        await execute_user_broadcast(bot, query.message.chat.id, user_id, b_msg, is_pin)
    elif broadcast_type == "groups":
        await execute_group_broadcast(bot, query.message.chat.id, user_id, b_msg, is_pin)
    
    # Clear pending data
    del pending_broadcasts[user_id]
    await query.answer()

async def execute_user_broadcast(bot, chat_id, user_id, b_msg, is_pin):
    """Execute user broadcast"""
    users = [user async for user in await db.get_all_users()]
    total_users = len(users)
    status_msg = await bot.send_message(chat_id, "📤 <b>Broadcasting your message...</b>")
    success = blocked = deleted = failed = 0
    start_time = time.time()
    cancelled = False

    async def send(user):
        try:
            _, result = await users_broadcast(int(user["id"]), b_msg, is_pin)
            return result
        except FloodWait as e:
            logging.warning(f"FloodWait: {e.value} seconds")
            await asyncio.sleep(e.value)
            return "Error"
        except Exception as e:
            logging.exception(f"Error sending broadcast to {user['id']}")
            return "Error"

    async with lock:
        for i in range(0, total_users, 100):
            if temp.B_USERS_CANCEL:
                temp.B_USERS_CANCEL = False
                cancelled = True
                break
            batch = users[i:i + 100]
            results = await asyncio.gather(*[send(user) for user in batch])

            for res in results:
                if res == "Success":
                    success += 1
                elif res == "Blocked":
                    blocked += 1
                elif res == "Deleted":
                    deleted += 1
                elif res == "Error":
                    failed += 1

            done = i + len(batch)
            elapsed = get_readable_time(time.time() - start_time)
            
            try:
                await status_msg.edit(
                    f"📣 <b>Broadcast Progress....:</b>\n\n"
                    f"👥 Total: <code>{total_users}</code>\n"
                    f"✅ Done: <code>{done}</code>\n"
                    f"📬 Success: <code>{success}</code>\n"
                    f"⛔ Blocked: <code>{blocked}</code>\n"
                    f"🗑️ Deleted: <code>{deleted}</code>\n"
                    f"⏱️ Time: {elapsed}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel#users")]
                    ])
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
            
            await asyncio.sleep(0.1)
    
    elapsed = get_readable_time(time.time() - start_time)
    final_status = (
        f"{'❌ <b>Broadcast Cancelled.</b>' if cancelled else '✅ <b>Broadcast Completed.</b>'}\n\n"
        f"🕒 Time: {elapsed}\n"
        f"👥 Total: <code>{total_users}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"⛔ Blocked: <code>{blocked}</code>\n"
        f"🗑️ Deleted: <code>{deleted}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )
    await status_msg.edit(final_status)

async def execute_group_broadcast(bot, chat_id, user_id, b_msg, is_pin):
    """Execute group broadcast"""
    chats = await db.get_all_chats()
    total_chats = await db.total_chat_count()
    status_msg = await bot.send_message(chat_id, "📤 <b>Broadcasting your message to groups...</b>")
    start_time = time.time()
    done = success = failed = 0
    cancelled = False

    async with lock:
        async for chat in chats:
            time_taken = get_readable_time(time.time() - start_time)
            if temp.B_GROUPS_CANCEL:
                temp.B_GROUPS_CANCEL = False
                cancelled = True
                break
            try:
                sts = await groups_broadcast(int(chat['id']), b_msg, is_pin)
            except FloodWait as e:
                logging.warning(f"FloodWait: {e.value} seconds")
                await asyncio.sleep(e.value)
                sts = 'Error'
            except Exception as e:
                logging.exception(f"Error broadcasting to group {chat['id']}")
                sts = 'Error'
            
            if sts == "Success":
                success += 1
            else:
                failed += 1
            done += 1
            
            if done % 10 == 0:
                btn = [[InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel#groups")]]
                try:
                    await status_msg.edit(
                        f"📣 <b>Group broadcast progress:</b>\n\n"
                        f"👥 Total Groups: <code>{total_chats}</code>\n"
                        f"✅ Completed: <code>{done} / {total_chats}</code>\n"
                        f"📬 Success: <code>{success}</code>\n"
                        f"❌ Failed: <code>{failed}</code>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass
    
    time_taken = get_readable_time(time.time() - start_time)
    final_text = (
        f"{'❌ <b>Groups broadcast cancelled!</b>' if cancelled else '✅ <b>Group broadcast completed.</b>'}\n"
        f"⏱️ Completed in {time_taken}\n\n"
        f"👥 Total Groups: <code>{total_chats}</code>\n"
        f"✅ Completed: <code>{done} / {total_chats}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )
    try:
        await status_msg.edit(final_text)
    except MessageTooLong:
        with open("reason.txt", "w+") as outfile:
            outfile.write(str(failed))
        await bot.send_document(
            chat_id, "reason.txt", caption=final_text
        )
        os.remove("reason.txt")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.private)
async def broadcast_users(bot, message):
    """Start user broadcast with inline buttons"""
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    if lock.locked():
        return await message.reply("⚠️ Another broadcast is in progress. Please wait...")
    
    # Store broadcast data
    pending_broadcasts[message.from_user.id] = {
        'message': message.reply_to_message,
        'type': 'users'
    }
    
    # Ask with inline buttons
    await message.reply(
        "<b>Do you want to pin this message in users?</b>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="pin_choice#yes#users"),
                InlineKeyboardButton("❌ No", callback_data="pin_choice#no#users")
            ]
        ])
    )

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.private)
async def broadcast_group(bot, message):
    """Start group broadcast with inline buttons"""
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to group broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    # Store broadcast data
    pending_broadcasts[message.from_user.id] = {
        'message': message.reply_to_message,
        'type': 'groups'
    }
    
    # Ask with inline buttons
    await message.reply(
        "<b>Do you want to pin this message in groups?</b>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="pin_choice#yes#groups"),
                InlineKeyboardButton("❌ No", callback_data="pin_choice#no#groups")
            ]
        ])
    )

@Client.on_message(filters.command("clear_junk") & filters.user(ADMINS))
async def remove_junkuser__db(bot, message):
    users = await db.get_all_users()
    b_msg = message 
    sts = await message.reply_text('ɪɴ ᴘʀᴏɢʀᴇss.... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ')   
    start_time = time.time()
    total_users = await db.total_users_count()
    blocked = 0
    deleted = 0
    failed = 0
    done = 0
    
    async for user in users:
        try:
            pti, sh = await clear_junk(int(user['id']), b_msg)
            if pti == False:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            logging.exception(f"Error in clear_junk for user {user['id']}")
            failed += 1
        
        done += 1
        if done % 50 == 0:
            try:
                await sts.edit(f"In Progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}")
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    await bot.send_message(message.chat.id, f"Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}")

@Client.on_message(filters.command(["junk_group", "clear_junk_group"]) & filters.user(ADMINS))
async def junk_clear_group(bot, message):
    groups = await db.get_all_chats()
    if not groups:
        grp = await message.reply_text("❌ Nᴏ ɢʀᴏᴜᴘs ғᴏᴜɴᴅ ғᴏʀ ᴄʟᴇᴀʀ Jᴜɴᴋ ɢʀᴏᴜᴘs.")
        await asyncio.sleep(60)
        await grp.delete()
        return
    
    b_msg = message
    sts = await message.reply_text(text='..............')
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = ""
    deleted = 0
    
    async for group in groups:
        try:
            pti, sh, ex = await junk_group(int(group['id']), b_msg)        
            if pti == False:
                if sh == "deleted":
                    deleted += 1 
                    failed += ex 
                    try:
                        await bot.leave_chat(int(group['id']))
                    except Exception as e:
                        print(f"{e} > {group['id']}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            logging.exception(f"Error in junk_group for {group['id']}")
        
        done += 1
        if done % 50 == 0:
            try:
                await sts.edit(f"in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}")
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    
    try:
        await bot.send_message(message.chat.id, f"Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}\n\nFiled Reson:- {failed}")    
    except MessageTooLong:
        with open('junk.txt', 'w+') as outfile:
            outfile.write(failed)
        await message.reply_document('junk.txt', caption=f"Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}")
        os.remove("junk.txt")
