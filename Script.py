class script(object):
    # START MESSAGE WITH ⏳ ANIMATION
    START_TXT = """<b>ʜᴇʏ, {}!
ɪ'ᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ TORRENT ➝ FILE ʙᴏᴛ 🌐</b>

<b>ᴅᴏᴡɴʟᴏᴀᴅ ғɪʟᴇs ғʀᴏᴍ MAGNET & TORRENT 🧲</b>
<b>ᴊᴜsᴛ sᴇɴᴅ ᴀ MAGNET LINK / TORRENT FILE ⚡</b>"""

    GSTART_TXT = """<b>ʜᴇʏ, {}! ⏳</b>
<b>ɪ'ᴍ ᴀ ғᴀsᴛ TORRENT DOWNLOADER 🤖</b>
<b>ᴅᴏᴡɴʟᴏᴀᴅ ғɪʟᴇs ᴜᴘ ᴛᴏ 𝟺GB 💎</b>
<b>Premium users get ultra-fast download 🚀</b>"""

    HELP_TXT = """<b>
✨ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ TORRENT FILES ✨

1️⃣ Send a MAGNET LINK 🧲 or TORRENT FILE 📄
2️⃣ Wait for download ⏳
3️⃣ Get files uploaded to Telegram 📂

📌 ғᴇᴀᴛᴜʀᴇs:
➤ Download from Magnet & Torrent 🌐
➤ Auto upload files to Telegram 📤
➤ Free limit: 𝟸GB 💾
➤ Premium limit: 𝟺GB 🚀
➤ Fast download for premium ⚡
➤ Supports all file types 📁
➤ Forced subscription enabled
</b>"""

    ABOUT_TXT = """<b>╭────[ ʙᴏᴛ ᴅᴇᴛᴀɪʟs ]────⍟
├⍟ Mʏ Nᴀᴍᴇ : <a href=https://t.me/{}>{}</a>
├⍟ Dᴇᴠᴇʟᴏᴘᴇʀ : <a href=https://t.me/Venuboyy>Zᴇʀᴏᴅᴇᴠ</a>
├⍟ Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a>
├⍟ Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/'>ᴘʏᴛʜᴏɴ 𝟹</a>
├⍟ Dᴀᴛᴀʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a>
├⍟ Fɪʟᴇ Lɪᴍɪᴛ : Free 𝟸GB | Premium 𝟺GB 💾
├⍟ Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ1.0 [ ꜱᴛᴀʙʟᴇ ]
╰───────────────⍟</b>"""

    # Premium Messages
    BPREMIUM_TXT = """<b>💎 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs 💎

✨ Get Premium and enjoy:
➤ Download up to 4GB files 🚀
➤ Faster download speed ⚡
➤ No daily limits 🎯
➤ Priority support 💬

💰 Available Plans:
• 7 Days - 50⭐
• 1 Month - 100⭐
• 3 Months - 250⭐
• 6 Months - 500⭐
• 1 Year - 1000⭐

👉 Choose your plan below!</b>"""

    PREMIUM_END_TEXT = """<b>❌ Your premium has expired, {}!

To continue enjoying premium features, renew now! 💎</b>"""

    # Download Progress
    DOWNLOAD_PROGRESS = """⬇️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴...

{progress_bar}

📁 Total Size : {total_size}
📥 Downloaded : {downloaded}
📊 Progress : {percentage}%
⚡ Speed : {speed}
⏳ Remaining : {eta}"""

    UPLOAD_PROGRESS = """⬆️ 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴...

{progress_bar}

📁 Total Size : {total_size}
📤 Uploaded : {uploaded}
📊 Progress : {percentage}%
⚡ Speed : {speed}
⏳ Remaining : {eta}"""

    # Force Subscribe Message
    FORCE_SUB_TEXT = """<b>❌ Access Denied!

You must join our channels to use this bot.

📢 Join all channels below and try again:
{channels}

Then click on "🔄 Try Again" button!</b>"""

    # User Info
    USER_INFO = """<b>👤 ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ

🆔 User ID: <code>{user_id}</code>
👤 Name: {name}
📅 Joined: {joined_date}
💎 Premium: {premium_status}
📊 Downloads: {downloads}
📦 Total Downloaded: {total_data}</b>"""

    PREMIUM_USER_INFO = """<b>👤 ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ

🆔 User ID: <code>{user_id}</code>
👤 Name: {name}
📅 Joined: {joined_date}
💎 Premium: ✅ Active
⏰ Expires: {expiry_date}
⏳ Time Left: {time_left}
📊 Downloads: {downloads}
📦 Total Downloaded: {total_data}</b>"""

    # Error Messages
    SIZE_LIMIT_EXCEEDED = """<b>❌ File size limit exceeded!

📁 File Size: {file_size}
⚠️ Your Limit: {user_limit}

💎 Upgrade to Premium for 4GB limit!</b>"""

    TORRENT_ERROR = """<b>❌ Error downloading torrent!

Error: {error}

Please try again with a valid torrent/magnet link.</b>"""
