import time
import math
import os
import asyncio
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

class temp:
    B_USERS_CANCEL = False
    B_GROUPS_CANCEL = False
    B_LINK = ""

def get_readable_time(seconds):
    """Convert seconds to readable time format"""
    periods = [
        ('d', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    ]
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{int(period_value)}{period_name}")
    return ' '.join(result) if result else '0s'

def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def progress_bar(percentage):
    """Create a progress bar"""
    filled = int(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return bar

async def get_seconds(time_str):
    """Convert time string to seconds"""
    try:
        time_amount = int(time_str.split()[0])
        time_unit = time_str.split()[1].lower()
        
        if time_unit in ["second", "seconds", "sec", "s"]:
            return time_amount
        elif time_unit in ["minute", "minutes", "min", "m"]:
            return time_amount * 60
        elif time_unit in ["hour", "hours", "hr", "h"]:
            return time_amount * 3600
        elif time_unit in ["day", "days", "d"]:
            return time_amount * 86400
        elif time_unit in ["week", "weeks", "w"]:
            return time_amount * 604800
        elif time_unit in ["month", "months", "mon"]:
            return time_amount * 2592000
        elif time_unit in ["year", "years", "y"]:
            return time_amount * 31536000
        else:
            return 0
    except:
        return 0

async def users_broadcast(user_id, message, pin):
    """Broadcast message to user"""
    try:
        if pin:
            await message.copy(chat_id=user_id)
            msg = await message.copy(chat_id=user_id)
            await msg.pin(disable_notification=True)
        else:
            await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await users_broadcast(user_id, message, pin)
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except Exception as e:
        return False, "Error"

async def groups_broadcast(chat_id, message, pin):
    """Broadcast message to group"""
    try:
        if pin:
            await message.copy(chat_id=chat_id)
            msg = await message.copy(chat_id=chat_id)
            await msg.pin(disable_notification=True)
        else:
            await message.copy(chat_id=chat_id)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await groups_broadcast(chat_id, message, pin)
    except Exception as e:
        return "Error"

async def clear_junk(user_id, message):
    """Check if user is blocked/deleted"""
    try:
        await message._client.send_chat_action(user_id, "typing")
        return True, "Active"
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except Exception as e:
        return False, "Error"

async def junk_group(chat_id, message):
    """Check if group is valid"""
    try:
        await message._client.send_chat_action(chat_id, "typing")
        return True, "Active", ""
    except Exception as e:
        return False, "deleted", str(e)

async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Progress callback for pyrogram uploads/downloads"""
    now = time.time()
    diff = now - start
    if diff < 1:
        return

    percentage = current * 100 / total
    speed = current / diff
    elapsed_time = round(diff)
    time_to_completion = round((total - current) / speed) if speed > 0 else 0
    
    progress = progress_bar(percentage)
    
    if ud_type == "downloading":
        from Script import script
        text = script.DOWNLOAD_PROGRESS.format(
            progress_bar=progress,
            total_size=humanbytes(total),
            downloaded=humanbytes(current),
            percentage=round(percentage, 2),
            speed=f"{humanbytes(speed)}/s",
            eta=get_readable_time(time_to_completion)
        )
    else:
        from Script import script
        text = script.UPLOAD_PROGRESS.format(
            progress_bar=progress,
            total_size=humanbytes(total),
            uploaded=humanbytes(current),
            percentage=round(percentage, 2),
            speed=f"{humanbytes(speed)}/s",
            eta=get_readable_time(time_to_completion)
        )
    
    try:
        await message.edit_text(text)
    except:
        pass
