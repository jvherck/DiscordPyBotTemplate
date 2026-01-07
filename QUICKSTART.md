# Quick Start Guide

Get your Discord bot running in under 5 minutes!

## 🚀 Fast Track Setup

### 1. Get Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Enable these Privileged Gateway Intents:
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 2. Install & Configure

```bash
# Clone and enter directory
cd DiscordPyBotTemplate

# Run setup script
python scripts/setup.py

# Install dependencies
pip install -r requirements.txt

# Configure your token
# Edit .env and set DISCORD_TOKEN=your_token_here
```

### 3. Run the Bot

```bash
# Production mode
python main.py

# Development mode (with debug logging)
python scripts/run_dev.py

# With Docker
docker-compose up -d
```

### 4. Invite Your Bot

Use this URL (replace CLIENT_ID with your Application ID):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

## 📝 First Commands to Try

Once your bot is running and invited to a server:

```
!ping          - Check if bot is responsive
!info          - Show bot information
!serverinfo    - Show server details
/ping          - Slash command version
/info          - Slash command version
```

## 🛠️ Essential Configuration

Edit `.env` file:

```env
# Required
DISCORD_TOKEN=your_bot_token_here

# Recommended
DISCORD_PREFIX=!
BOT_NAME=MyAwesomeBot
ENVIRONMENT=development

# Optional (defaults work fine)
LOG_LEVEL=INFO
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///data/bot.db
```

## 🎯 Next Steps

### Add Custom Commands

1. Create a new file in `bot/cogs/` (e.g., `mycog.py`)
2. Copy the structure from `examples/custom_cog.py`
3. Restart the bot - it auto-loads!

### Use the Database

```python
# In your cog
from bot.database.models import UserData

# Get user data
user = await self.bot.db.get(UserData, user_id, "user_id")

# Create new data
new_user = UserData(user_id=123, username="Test")
await self.bot.db.create(new_user)
```

### Customize Your Bot

```python
# In main.py, customize the config
from bot import DiscordBot, BotConfig

config = BotConfig()
config.discord_prefix = "?"
config.presence_text = "my custom status"

bot = DiscordBot(config=config)
bot.run_bot()
```

## 🐛 Troubleshooting

**Bot offline?**
- Check token is correct in `.env`
- Verify intents are enabled in Developer Portal

**Commands not working?**
- Check prefix: `!ping` not `?ping`
- Enable Message Content Intent
- Use `/ping` for slash commands

**Database errors?**
- Ensure `data/` directory exists
- Check file permissions
- Use `!dbhealth` to test connection

**Slash commands not showing?**
- Run `!sync` command (takes up to 1 hour globally)
- Use `!sync ~` for instant guild-specific sync

## 📚 Learn More

- **Full documentation:** See [README.md](README.md)
- **Examples:** Check [examples/](examples/) directory
- **Discord.py docs:** [discordpy.readthedocs.io](https://discordpy.readthedocs.io/)
- **Support:** [discord.gg/dpy](https://discord.gg/dpy)

## 🎉 You're Ready!

Your bot is now running with:
- ✅ Professional logging
- ✅ Database integration
- ✅ Error handling
- ✅ Command tracking
- ✅ Auto-loading cogs
- ✅ Docker support

Start building your features! 🚀
