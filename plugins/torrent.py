import os
import asyncio
import time
import libtorrent as lt
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Script import script
from config import config
from database.users_chats_db import db
from utils import humanbytes, progress_for_pyrogram, get_readable_time

# Store active downloads
active_downloads = {}

def create_modern_progress_bar(percentage, length=20):
    """Create a modern animated progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    
    # Using modern block characters for smoother appearance
    bar = '█' * filled + '░' * empty
    return f"[{bar}]"

def format_progress_message(s, total_size, start_time):
    """Format download progress with modern UI"""
    progress = s.progress * 100
    downloaded = s.total_done
    download_speed = s.download_rate
    upload_speed = s.upload_rate
    peers = s.num_peers
    seeds = s.num_seeds
    
    # Calculate ETA
    if download_speed > 0:
        eta = (total_size - downloaded) / download_speed
        eta_str = get_readable_time(int(eta))
    else:
        eta_str = "Calculating..."
    
    # Calculate elapsed time
    elapsed = time.time() - start_time
    elapsed_str = get_readable_time(int(elapsed))
    
    # Create progress bar
    progress_bar = create_modern_progress_bar(progress)
    
    # Format message with modern UI
    message = f"""
╭─────────────────────╮
│   📥 DOWNLOADING    │
╰─────────────────────╯

{progress_bar}
⚡ Progress: {progress:.1f}%

📊 Downloaded: {humanbytes(downloaded)} / {humanbytes(total_size)}

⬇️ Speed: {humanbytes(download_speed)}/s
⬆️ Upload: {humanbytes(upload_speed)}/s

🌱 Seeds: {seeds} | 👥 Peers: {peers}

⏱ ETA: {eta_str}
⏳ Elapsed: {elapsed_str}
"""
    return message

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
    
    # Setup libtorrent session with optimized settings
    ses = lt.session()
    
    # Apply optimized settings for faster downloads
    settings = {
        # Connection settings
        'connections_limit': 500,
        'active_downloads': 10,
        'active_seeds': 10,
        'active_limit': 15,
        
        # Speed settings
        'download_rate_limit': 0,  # No limit
        'upload_rate_limit': 0,    # No limit
        
        # Peer settings
        'max_peerlist_size': 4000,
        'min_reconnect_time': 2,
        'peer_connect_timeout': 7,
        
        # Optimize for speed
        'enable_outgoing_utp': True,
        'enable_incoming_utp': True,
        'enable_outgoing_tcp': True,
        'enable_incoming_tcp': True,
        
        # DHT and peer exchange
        'enable_dht': True,
        'enable_lsd': True,
        'enable_natpmp': True,
        'enable_upnp': True,
        
        # Disk cache (increase for better performance)
        'cache_size': 512,  # 512 MB
        'use_read_cache': True,
        
        # Request queue optimization
        'max_allowed_in_request_queue': 2000,
        'max_out_request_queue': 1500,
        
        # Piece timeout
        'piece_timeout': 10,
        'request_timeout': 30,
        
        # Choking algorithm
        'choking_algorithm': lt.settings_pack.fixed_slots_choker,
        'seed_choking_algorithm': lt.settings_pack.fastest_upload,
    }
    
    ses.apply_settings(settings)
    
    # Listen on multiple ports for better connectivity
    ses.listen_on(6881, 6891)
    
    params = {
        'save_path': download_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        # Set high priority for all files
        'flags': lt.torrent_flags.auto_managed | lt.torrent_flags.duplicate_is_error,
    }
    
    # Add torrent
    if magnet_link:
        handle = lt.add_magnet_uri(ses, magnet_link, params)
    else:
        info = lt.torrent_info(torrent_file)
        handle = ses.add_torrent({'ti': info, 'save_path': download_path})
    
    # Set sequential download for better streaming
    handle.set_sequential_download(True)
    
    status_msg = await message.reply("🔍 Fetching torrent metadata...\n⏳ Please wait...")
    
    # Wait for metadata with timeout
    timeout = 60  # 60 seconds timeout
    waited = 0
    while not handle.has_metadata():
        await asyncio.sleep(1)
        waited += 1
        if waited > timeout:
            await status_msg.edit("❌ Timeout: Could not fetch metadata!")
            ses.remove_torrent(handle)
            return
        if waited % 5 == 0:
            await status_msg.edit(f"🔍 Fetching metadata... ({waited}s)")
    
    torrent_info = handle.get_torrent_info()
    total_size = torrent_info.total_size()
    torrent_name = torrent_info.name()
    
    # Check size limit
    if total_size > user_limit:
        await status_msg.delete()
        await message.reply(
            f"❌ **File size exceeds limit!**\n\n"
            f"📁 File Size: `{humanbytes(total_size)}`\n"
            f"⚠️ Your Limit: `{humanbytes(user_limit)}`\n\n"
            f"💡 Upgrade to premium for larger downloads!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")]
            ])
        )
        ses.remove_torrent(handle)
        return
    
    # Prioritize all pieces for faster download
    handle.prioritize_pieces([7] * torrent_info.num_pieces())
    
    await status_msg.edit(
        f"✅ **Metadata Received**\n\n"
        f"📝 Name: `{torrent_name}`\n"
        f"📦 Size: `{humanbytes(total_size)}`\n\n"
        f"⬇️ Starting download..."
    )
    
    # Download progress
    start_time = time.time()
    active_downloads[user_id] = handle
    last_update = 0
    
    while not handle.is_seed():
        s = handle.status()
        
        if user_id not in active_downloads:
            # Download cancelled
            ses.remove_torrent(handle)
            await status_msg.edit("❌ Download cancelled!")
            return
        
        # Update every 3 seconds to avoid rate limits
        current_time = time.time()
        if current_time - last_update >= 3:
            try:
                progress_text = format_progress_message(s, total_size, start_time)
                await status_msg.edit(progress_text)
                last_update = current_time
            except Exception as e:
                # Ignore edit errors (message not modified, rate limit, etc.)
                pass
        
        await asyncio.sleep(1)
    
    del active_downloads[user_id]
    await status_msg.edit(
        "✅ **Download Complete!**\n\n"
        "📤 Preparing to upload files to Telegram...\n"
        "⏳ Please wait..."
    )
    
    # Upload files
    files = []
    for root, dirs, filenames in os.walk(download_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            files.append(filepath)
    
    uploaded_count = 0
    total_files = len(files)
    
    for filepath in files:
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        # Skip very small files (less than 1KB)
        if file_size < 1024:
            continue
        
        upload_msg = await message.reply(
            f"📤 **Uploading** ({uploaded_count + 1}/{total_files})\n\n"
            f"📄 `{filename}`\n"
            f"💾 Size: `{humanbytes(file_size)}`"
        )
        
        try:
            start = time.time()
            
            # Determine file type and upload
            if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv')):
                await message.reply_video(
                    video=filepath,
                    caption=f"📹 **{filename}**\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("📤 Uploading", upload_msg, start),
                    supports_streaming=True
                )
            elif filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')):
                await message.reply_audio(
                    audio=filepath,
                    caption=f"🎵 **{filename}**\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("📤 Uploading", upload_msg, start)
                )
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                await message.reply_photo(
                    photo=filepath,
                    caption=f"🖼 **{filename}**\n💾 {humanbytes(file_size)}"
                )
            else:
                await message.reply_document(
                    document=filepath,
                    caption=f"📄 **{filename}**\n💾 {humanbytes(file_size)}",
                    progress=progress_for_pyrogram,
                    progress_args=("📤 Uploading", upload_msg, start)
                )
            
            await upload_msg.delete()
            uploaded_count += 1
            
        except Exception as e:
            await upload_msg.edit(f"❌ **Upload Failed**\n\n📄 {filename}\n⚠️ Error: `{str(e)}`")
    
    # Update user stats
    await db.update_download_stats(user_id, total_size)
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(download_path, ignore_errors=True)
        if torrent_file and os.path.exists(torrent_file):
            os.remove(torrent_file)
    except:
        pass
    
    # Final success message
    await status_msg.delete()
    
    total_time = get_readable_time(int(time.time() - start_time))
    await message.reply(
        f"✅ **All Done!**\n\n"
        f"📊 Files Uploaded: `{uploaded_count}/{total_files}`\n"
        f"💾 Total Size: `{humanbytes(total_size)}`\n"
        f"⏱ Time Taken: `{total_time}`\n\n"
        f"Thank you for using our service! 🎉"
    )

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_download(client, message):
    user_id = message.from_user.id
    
    if user_id in active_downloads:
        del active_downloads[user_id]
        await message.reply(
            "✅ **Download Cancelled!**\n\n"
            "The torrent download has been stopped."
        )
    else:
        await message.reply(
            "❌ **No Active Download**\n\n"
            "You don't have any active downloads to cancel."
        )

@Client.on_message(filters.command("stats") & filters.private)
async def download_stats(client, message):
    """Show download statistics"""
    user_id = message.from_user.id
    
    if user_id in active_downloads:
        handle = active_downloads[user_id]
        s = handle.status()
        
        stats_msg = f"""
📊 **Current Download Stats**

⚡ Progress: {s.progress * 100:.1f}%
⬇️ Download: {humanbytes(s.download_rate)}/s
⬆️ Upload: {humanbytes(s.upload_rate)}/s
🌱 Seeds: {s.num_seeds}
👥 Peers: {s.num_peers}
💾 Downloaded: {humanbytes(s.total_done)}

Use /cancel to stop the download.
"""
        await message.reply(stats_msg)
    else:
        await message.reply("❌ No active download found!")
