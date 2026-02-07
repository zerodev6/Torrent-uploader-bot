# 🚀 Complete Setup Guide for Torrent Bot

## 📋 Prerequisites

Before starting, you need:

1. **Telegram Account** - A phone number with Telegram
2. **Telegram Bot Token** - From @BotFather
3. **API Credentials** - From https://my.telegram.org
4. **MongoDB Database** - Free from MongoDB Atlas
5. **Server/VPS** - Or your local machine with Python 3.8+

---

## Step 1️⃣: Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions:
   - Enter bot name (e.g., "My Torrent Bot")
   - Enter bot username (must end with 'bot', e.g., "mytorrent_bot")
4. **Save the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## Step 2️⃣: Get API ID and API Hash

1. Go to https://my.telegram.org
2. Login with your phone number
3. Click on "API Development Tools"
4. Fill in the form (any app title and short name)
5. **Save API ID and API Hash**

---

## Step 3️⃣: Setup MongoDB Database

### Option A: MongoDB Atlas (Recommended - Free)

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create a new cluster (Free M0)
4. Wait for cluster to be created (~5 minutes)
5. Click "Connect" on your cluster
6. Add connection IP:
   - Click "Add a Different IP Address"
   - Enter `0.0.0.0/0` (allows all IPs)
   - Click "Add IP Address"
7. Create Database User:
   - Enter username and password
   - Click "Create Database User"
8. Click "Choose a connection method"
9. Select "Connect your application"
10. Copy the connection string (looks like):
    ```
    mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
    ```
11. Replace `<password>` with your actual password

### Option B: Local MongoDB

```bash
# Install MongoDB on Ubuntu/Debian
sudo apt update
sudo apt install mongodb-server
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Your connection string will be:
# mongodb://localhost:27017
```

---

## Step 4️⃣: Setup Force Subscribe Channels

1. Create your Telegram channels (if you don't have them)
2. Make your bot an admin in those channels
3. Note down the channel usernames (without @)
   - Example: `zerodev2`, `mvxyoffcail`

---

## Step 5️⃣: Install the Bot

### On Ubuntu/Debian Server:

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Extract bot files
tar -xzf torrent_bot.tar.gz
cd torrent_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### On Windows:

1. Install Python 3.8+ from python.org
2. Extract `torrent_bot.tar.gz` using 7-Zip or WinRAR
3. Open Command Prompt in the bot folder
4. Run:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 6️⃣: Configure the Bot

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file:
```bash
nano .env  # On Linux
notepad .env  # On Windows
```

3. Fill in ALL required values:

```env
# === REQUIRED CONFIGURATION ===

# From Step 2
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# From Step 1
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# From Step 3
DATABASE_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=torrent_bot

# Your Telegram User ID (get from @userinfobot)
OWNER_ID=123456789
ADMINS=123456789 987654321

# Your Telegram username
OWNER_USERNAME=@Venuboyy

# From Step 4 (comma separated, no spaces, no @)
FORCE_SUB_CHANNELS=zerodev2,mvxyoffcail

# === OPTIONAL CONFIGURATION ===

# Channel for premium purchase logs
PREMIUM_LOGS=-1001234567890

# Download limits in bytes (default 2GB and 4GB)
FREE_LIMIT=2147483648
PREMIUM_LIMIT=4294967296
```

4. Save the file:
   - **Linux**: Press `Ctrl+X`, then `Y`, then `Enter`
   - **Windows**: Click `File > Save`

---

## Step 7️⃣: Run the Bot

### Quick Start:

```bash
# Make start script executable
chmod +x start.sh

# Run the bot
./start.sh
```

### Manual Start:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# Run bot
python bot.py
```

### Run in Background (Linux):

```bash
# Using screen
screen -S torrent_bot
python bot.py
# Press Ctrl+A then D to detach

# To reattach:
screen -r torrent_bot

# Using nohup
nohup python bot.py > bot.log 2>&1 &

# Using systemd service
sudo nano /etc/systemd/system/torrent-bot.service
```

Example systemd service:
```ini
[Unit]
Description=Torrent Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/torrent_bot
Environment="PATH=/home/your_username/torrent_bot/venv/bin"
ExecStart=/home/your_username/torrent_bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable torrent-bot
sudo systemctl start torrent-bot
sudo systemctl status torrent-bot
```

---

## Step 8️⃣: Test the Bot

1. Open Telegram and find your bot
2. Send `/start` command
3. Join the required channels
4. Try sending a magnet link or torrent file

**Test Magnet Link:**
```
magnet:?xt=urn:btih:DD8255ECDC7CA55FB0BBF81323D87062DB1F6D1C&dn=Big+Buck+Bunny&tr=udp%3A%2F%2Fexplodie.org%3A6969
```

---

## 🔧 Troubleshooting

### Bot Not Starting

**Error: ModuleNotFoundError**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Error: Invalid bot token**
- Check BOT_TOKEN in .env file
- Make sure there are no extra spaces
- Get a new token from @BotFather

### Bot Started But Not Responding

**Check if bot is running:**
```bash
ps aux | grep python  # Linux
tasklist | findstr python  # Windows
```

**Check logs for errors:**
```bash
tail -f bot.log  # If using nohup
```

**Force Subscribe Not Working:**
- Make sure bot is admin in channels
- Check channel usernames in .env
- Channel usernames should NOT have @

### Database Connection Failed

**Error: ServerSelectionTimeoutError**
- Check DATABASE_URI is correct
- Verify MongoDB cluster is running
- Check IP whitelist in MongoDB Atlas

**Fix:**
1. Go to MongoDB Atlas
2. Network Access → Add IP Address → 0.0.0.0/0

### Downloads Not Working

**Error: Permission Denied**
```bash
# Create downloads folder
mkdir -p downloads
chmod 777 downloads
```

**Error: File size limit exceeded**
- For files >2GB, user needs premium
- Increase FREE_LIMIT or PREMIUM_LIMIT in .env

---

## 📱 Admin Commands Quick Reference

```bash
# Premium Management
/add_premium <user_id> <time>
  Example: /add_premium 123456789 1 month

/remove_premium <user_id>
/get_premium <user_id>
/premium_users

# Broadcast
/broadcast - Reply to a message
/grp_broadcast - Broadcast to groups

# Bot Management
/status - System status
/stats - Bot statistics
/clear_junk - Remove blocked users
/clear_junk_group - Remove dead groups
```

---

## 🎯 Premium Time Formats

When using `/add_premium`, you can use:

```bash
/add_premium 123456789 7 days
/add_premium 123456789 1 month
/add_premium 123456789 3 months
/add_premium 123456789 6 months
/add_premium 123456789 1 year
/add_premium 123456789 24 hours
/add_premium 123456789 30 minutes
```

---

## 🔐 Security Best Practices

1. **Never share your `.env` file**
2. **Never commit `.env` to git**
3. **Use strong MongoDB password**
4. **Regularly update dependencies**
5. **Monitor logs for suspicious activity**
6. **Use firewall on your server**

---

## 📊 Monitoring & Maintenance

### Check Bot Status:
```bash
# View logs
tail -f bot.log

# Check memory usage
free -h

# Check disk space
df -h

# Monitor bot process
htop
```

### Update Bot:
```bash
# Stop bot
# Replace files
# Restart bot
systemctl restart torrent-bot
```

### Backup Database:
```bash
# MongoDB Atlas has automatic backups
# Manual backup:
mongodump --uri="your_mongodb_uri"
```

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide again
2. Review error messages in logs
3. Check if all configuration values are correct
4. Verify MongoDB connection
5. Join support channels: @zerodev2, @mvxyoffcail

---

## ✅ Final Checklist

Before going live, verify:

- [ ] Bot responds to `/start`
- [ ] Force subscribe works
- [ ] Can download small torrent
- [ ] Files upload to Telegram
- [ ] Premium system works
- [ ] Admin commands work
- [ ] Database is saving data
- [ ] Bot restarts automatically

---

## 🎉 Congratulations!

Your Torrent Bot is now ready! Share it with users and enjoy! 🚀

**Developer:** @Venuboyy (Zerodev)
