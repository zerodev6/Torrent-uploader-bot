import datetime
import time
import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.errors import FloodWait
from database.users_chats_db import db
from config import config
from utils import users_broadcast, groups_broadcast, temp, get_readable_time, clear_junk, junk_group
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

lock = asyncio.Lock()

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
async def pin_choice_callback(bot, query):
    _, choice, broadcast_type = query.data.split("#")
    
    is_pin = choice == "yes"
    
    await query.message.delete()
    
    if broadcast_type == "users":
        # Store the choice temporarily
        temp.PIN_CHOICE = is_pin
        temp.BROADCAST_MSG = query.message.reply_to_message
        
        # Start broadcasting
        await start_user_broadcast(bot, query.message, is_pin)
    elif broadcast_type == "groups":
        # Store the choice temporarily  
        temp.PIN_CHOICE = is_pin
        temp.BROADCAST_MSG = query.message.reply_to_message
        
        # Start group broadcasting
        await start_group_broadcast(bot, query.message, is_pin)

@Client.on_message(filters.command("broadcast") & filters.user(config.ADMINS) & filters.private)
async def broadcast_users(bot, message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    if lock.locked():
        return await message.reply("⚠️ Another broadcast is in progress. Please wait...")
    
    # Store the message to broadcast
    temp.BROADCAST_MSG = message.reply_to_message
    
    # Ask about pinning with inline buttons
    buttons = [
        [
            InlineKeyboardButton("📌 Yes", callback_data="pin_choice#yes#users"),
            InlineKeyboardButton("❌ No", callback_data="pin_choice#no#users")
        ]
    ]
    
    await message.reply(
        "<b>Do you want to pin this message in users?</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def start_user_broadcast(bot, message, is_pin):
    b_msg = temp.BROADCAST_MSG
    users = [user async for user in await db.get_all_users()]
    total_users = len(users)
    status_msg = await message.reply_text("📤 <b>Broadcasting your message...</b>")
    success = blocked = deleted = failed = 0
    start_time = time.time()
    cancelled = False

    async def send(user):
        try:
            _, result = await users_broadcast(int(user["id"]), b_msg, is_pin)
            return result
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
            except:
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


@Client.on_message(filters.command("grp_broadcast") & filters.user(config.ADMINS) & filters.private)
async def broadcast_group(bot, message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to group broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    # Store the message to broadcast
    temp.BROADCAST_MSG = message.reply_to_message
    
    # Ask about pinning with inline buttons
    buttons = [
        [
            InlineKeyboardButton("📌 Yes", callback_data="pin_choice#yes#groups"),
            InlineKeyboardButton("❌ No", callback_data="pin_choice#no#groups")
        ]
    ]
    
    await message.reply(
        "<b>Do you want to pin this message in groups?</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def start_group_broadcast(bot, message, is_pin):
    b_msg = temp.BROADCAST_MSG
    chats = await db.get_all_chats()
    total_chats = await db.total_chat_count()
    status_msg = await message.reply_text("📤 <b>Broadcasting your message to groups...</b>")
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
                except:
                    pass
    
    time_taken = get_readable_time(time.time() - start_time)
    text = (
        f"{'❌ <b>Groups broadcast cancelled!</b>' if cancelled else '✅ <b>Group broadcast completed.</b>'}\n"
        f"⏱️ Completed in {time_taken}\n\n"
        f"👥 Total Groups: <code>{total_chats}</code>\n"
        f"✅ Completed: <code>{done} / {total_chats}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )
    
    try:
        await status_msg.edit(text)
    except MessageTooLong:
        with open("reason.txt", "w+") as outfile:
            outfile.write(str(failed))
        await message.reply_document(
            "reason.txt", caption=text
        )
        os.remove("reason.txt")

@Client.on_message(filters.command("clear_junk") & filters.user(config.ADMINS))
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
        pti, sh = await clear_junk(int(user['id']), b_msg)
        if pti == False:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        
        if done % 50 == 0:
            try:
                await sts.edit(
                    f"In Progress:\n\n"
                    f"Total Users {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}"
                )
            except:
                pass
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    await bot.send_message(
        message.chat.id, 
        f"Completed:\nCompleted in {time_taken} seconds.\n\n"
        f"Total Users {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}"
    )

@Client.on_message(filters.command(["junk_group", "clear_junk_group"]) & filters.user(config.ADMINS))
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
        pti, sh, ex = await junk_group(int(group['id']), b_msg)        
        if pti == False:
            if sh == "deleted":
                deleted += 1 
                failed += ex 
                try:
                    await bot.leave_chat(int(group['id']))
                except Exception as e:
                    print(f"{e} > {group['id']}")  
        done += 1
        
        if done % 50 == 0:
            try:
                await sts.edit(
                    f"in progress:\n\n"
                    f"Total Groups {total_groups}\n"
                    f"Completed: {done} / {total_groups}\n"
                    f"Deleted: {deleted}"
                )
            except:
                pass
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    
    try:
        await bot.send_message(
            message.chat.id, 
            f"Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Groups {total_groups}\n"
            f"Completed: {done} / {total_groups}\n"
            f"Deleted: {deleted}\n\n"
            f"Filed Reson:- {failed}"
        )    
    except MessageTooLong:
        with open('junk.txt', 'w+') as outfile:
            outfile.write(failed)
        await message.reply_document(
            'junk.txt', 
            caption=f"Completed:\nCompleted in {time_taken} seconds.\n\n"
                    f"Total Groups {total_groups}\n"
                    f"Completed: {done} / {total_groups}\n"
                    f"Deleted: {deleted}"
        )
        os.remove("junk.txt")
