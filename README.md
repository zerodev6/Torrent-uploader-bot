# Torrent Downloader Telegram Bot

A powerful Telegram bot that downloads files from torrent and magnet links and uploads them directly to Telegram.

## Features

✨ **Core Features:**
- Download from Magnet Links & Torrent Files
- Auto upload to Telegram
- Progress tracking for downloads and uploads
- Support for all file types (video, audio, documents, images)
- Premium subscription system with Telegram Stars
- Force subscribe to channels
- Admin broadcast & management tools

📊 **User Features:**
- Free users: 2GB download limit
- Premium users: 4GB download limit
- User info & statistics
- Premium plans with Telegram Stars

🔧 **Admin Features:**
- Broadcast messages to users/groups
- User & group management
- Premium user management
- Bot statistics & status
- Clear junk users/groups

## Installation

### 1. Clone & Setup

```bash
# Extract the bot files
tar -xzf torrent_bot.tar.gz
cd torrent_bot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
nano .env
```

**Required Environment Variables:**

```env
# Get from https://my.telegram.org
API_ID=your_api_id
API_HASH=your_api_hash

# Get from @BotFather
BOT_TOKEN=your_bot_token

# MongoDB Connection String
DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net

# Admin User IDs (space separated)
ADMINS=123456789 987654321

# Owner Details
OWNER_ID=123456789
OWNER_USERNAME=@Venuboyy

# Force Subscribe Channels (comma separated, without @)
FORCE_SUB_CHANNELS=zerodev2,mvxyoffcail

# Optional: Premium Logs Channel ID
PREMIUM_LOGS=-1001234567890
```

### 3. MongoDB Setup

1. Create a free MongoDB cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new database user
3. Whitelist your IP (or use 0.0.0.0/0 for all IPs)
4. Copy the connection string and paste in `DATABASE_URI`

### 4. Pyrogram String Session (Optional)

If you want to use user client features, generate a string session:

```bash
python -c "from pyrogram import Client; import os; api_id = int(input('Enter API_ID: ')); api_hash = input('Enter API_HASH: '); Client(':memory:', api_id=api_id, api_hash=api_hash).run(lambda c: print(c.export_session_string()))"
```

Add the session string to `STRING_SESSION` in `.env`

### 5. Run the Bot

```bash
python bot.py
```

Or use screen/tmux for persistent running:

```bash
screen -S torrent_bot
python bot.py
# Press Ctrl+A then D to detach
```

## Bot Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/info` - Get your user information
- `/myplan` - Check your premium plan
- `/plan` - View premium plans
- `/cancel` - Cancel active download

### Admin Commands
- `/status` - Bot system status
- `/stats` - Detailed bot statistics
- `/broadcast` - Broadcast to all users
- `/grp_broadcast` - Broadcast to all groups
- `/add_premium <user_id> <time>` - Add premium to user
- `/remove_premium <user_id>` - Remove premium from user
- `/get_premium <user_id>` - Check user's premium status
- `/premium_users` - List all premium users
- `/clear_junk` - Remove blocked/deleted users
- `/clear_junk_group` - Remove inactive groups

## How to Use

### For Users:

1. Start the bot with `/start`
2. Join required channels if forced subscribe is enabled
3. Send a magnet link or .torrent file
4. Wait for download and upload to complete
5. Files will be sent to you in chat

### For Admins:

**Add Premium to User:**
```
/add_premium 123456789 1 month
```

**Broadcast Message:**
```
1. Reply to any message with /broadcast
2. Choose Yes/No for pinning
3. Monitor progress
```

## Premium Plans

Premium users get:
- 4GB file size limit (vs 2GB for free)
- Faster download priority
- No daily limits

**Available Plans:**
- 7 Days - 50⭐
- 1 Month - 100⭐
- 3 Months - 250⭐
- 6 Months - 500⭐
- 1 Year - 1000⭐

## File Structure

```
torrent_bot/
├── bot.py                 # Main bot file
├── config.py              # Configuration
├── Script.py              # Bot messages/scripts
├── requirements.txt       # Dependencies
├── .env.example          # Environment variables example
├── database/
│   └── users_chats_db.py # Database functions
├── plugins/
│   ├── start.py          # Start & welcome handlers
│   ├── torrent.py        # Torrent download handler
│   ├── premium.py        # Premium management
│   ├── broadcast.py      # Admin broadcast tools
│   └── info.py           # User info & stats
└── utils.py              # Utility functions
```

## Troubleshooting

**Bot not responding:**
- Check if bot token is correct
- Verify MongoDB connection
- Check logs for errors

**Downloads failing:**
- Ensure file size is within limit
- Check internet connection
- Verify magnet link/torrent is valid

**Premium payments not working:**
- Ensure Telegram Stars are enabled
- Check if payload format is correct
- Verify premium logs channel ID

## Developer

- **Developer:** @Venuboyy (Zerodev)
- **Support:** Join @zerodev2 & @mvxyoffcail

## License

This project is for educational purposes only. Use at your own risk.

## Credits

- Pyrogram Library
- LibTorrent
- MongoDB
