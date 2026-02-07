import os
import asyncio
import time
import libtorrent as lt
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Script import script
from config import config
from database.users_chats_db import db
from utils import humanbytes, progress_for_pyrogram, progress_bar, get_readable_time

# Store active downloads
active_downloads = {}

@Client.on_message(filters.private & (filters.regex(r"^magnet:\?xt=urn:") | filters.document))
async def handle_torrent(client, message):
    user_id = message.from_user.id
    
    # Check if user has access
    from plugins.start import check_force_sub
    if not await check_force_sub(client, message):
        return
    
    # Check if user is premium
    is_premium = await db.is_premium_user(user_id)
    user_limit = config.PREMIUM_LIMIT if is_premium else config.FREE_LIMIT
    
    # Get magnet link or torrent file
    magnet_link = None
    torrent_file = None
    
    if message.text and message.text.startswith("magnet:"):
        magnet_link = message.text
    elif message.document:
        if message.document.file_name.endswith('.torrent'):
            status = await message.reply("📥 Downloading torrent file...")
            torrent_file = await message.download(
                file_name=f"./downloads/{message.document.file_name}"
            )
            await status.delete()
        else:
            return await message.reply("❌ Please send a valid .torrent file!")
    else:
        return
    
    # Start download
    await download_torrent(client, message, magnet_link, torrent_file, user_limit, is_premium)

async def download_torrent(client, message, magnet_link, torrent_file, user_limit, is_premium):
    user_id = message.from_user.id
    
    # Create download directory
    download_path = f"./downloads/{user_id}_{int(time.time())}"
    os.makedirs(download_path, exist_ok=True)
    
    # Setup libtorrent session
    ses = lt.session()
    ses.listen_on(6881, 6891)
    
    params = {
        'save_path': download_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
    }
    
    # Add torrent
    if magnet_link:
        handle = lt.add_magnet_uri(ses, magnet_link, params)
    else:
        info = lt.torrent_info(torrent_file)
        handle = ses.add_torrent({'ti': info, 'save_path': download_path})
    
    status_msg = await message.reply("⏳ Fetching torrent metadata...")
    
    # Wait for metadata
    while not handle.has_metadata():
        await asyncio.sleep(1)
    
    torrent_info = handle.get_torrent_info()
    total_size = torrent_info.total_size()
    
    # Check size limit
    if total_size > user_limit:
        await status_msg.delete()
        await message.reply(
            script.SIZE_LIMIT_EXCEEDED.format(
                file_size=humanbytes(total_size),
                user_limit=humanbytes(user_limit)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")]
            ])
        )
        ses.remove_torrent(handle)
        return
    
    await status_msg.edit(f"⬇️ Starting download...\n📁 Size: {humanbytes(total_size)}")
    
    # Download progress
    start_time = time.time()
    active_downloads[user_id] = handle
    
    while not handle.is_seed():
        s = handle.status()
        
        if user_id not in active_downloads:
            # Download cancelled
            ses.remove_torrent(handle)
            await status_msg.edit("❌ Download cancelled!")
            return
        
        progress = s.progress * 100
        download_speed = s.download_rate
        downloaded = s.total_done
        eta = (total_size - downloaded) / download_speed if download_speed > 0 else 0
        
        progress_text = script.DOWNLOAD_PROGRESS.format(
            progress_bar=progress_bar(progress),
            total_size=humanbytes(total_size),
            downloaded=humanbytes(downloaded),
            percentage=round(progress, 2),
            speed=f"{humanbytes(download_speed)}/s",
            eta=get_readable_time(int(eta))
        )
        
        try:
            await status_msg.edit(progress_text)
        except:
            pass
        
        await asyncio.sleep(3)
    
    del active_downloads[user_id]
    await status_msg.edit("✅ Download completed! Uploading to Telegram...")
    
    # Upload files
    files = []
    for root, dirs, filenames in os.walk(download_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            files.append(filepath)
    
    for filepath in files:
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        upload_msg = await message.reply(f"⬆️ Uploading {filename}...")
        
        try:
            start = time.time()
            
            # Determine file type and upload
            if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):
                await message.reply_video(
                    video=filepath,
                    caption=f"📹 {filename}\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("uploading", upload_msg, start)
                )
            elif filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
                await message.reply_audio(
                    audio=filepath,
                    caption=f"🎵 {filename}\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("uploading", upload_msg, start)
                )
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                await message.reply_photo(
                    photo=filepath,
                    caption=f"🖼 {filename}\n💾 {humanbytes(file_size)}"
                )
            else:
                await message.reply_document(
                    document=filepath,
                    caption=f"📄 {filename}\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("uploading", upload_msg, start)
                )
            
            await upload_msg.delete()
        except Exception as e:
            await upload_msg.edit(f"❌ Error uploading {filename}: {str(e)}")
    
    # Update user stats
    await db.update_download_stats(user_id, total_size)
    
    # Cleanup
    import shutil
    shutil.rmtree(download_path, ignore_errors=True)
    if torrent_file and os.path.exists(torrent_file):
        os.remove(torrent_file)
    
    await status_msg.delete()
    await message.reply("✅ All files uploaded successfully!")

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_download(client, message):
    user_id = message.from_user.id
    
    if user_id in active_downloads:
        del active_downloads[user_id]
        await message.reply("✅ Download cancelled!")
    else:
        await message.reply("❌ No active download found!")
