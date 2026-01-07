# Discord Bot Template

A professional, enterprise-level Discord bot template built with Python 3.11+ and discord.py 2.6.4. This template provides a solid foundation for building scalable, maintainable Discord bots with modern best practices.

## Features

✨ **Core Features**
- 🤖 Built with discord.py 2.6.4 (latest version)
- 🐍 Python 3.11+ support (tested up to 3.14)
- ⚙️ Type-safe configuration management with Pydantic
- 🎨 Beautiful colored console logging with file rotation
- 📊 SQLAlchemy 2.0 with async support (SQLite & PostgreSQL)
- 🔄 Automatic cog/extension loading system
- 🛡️ Comprehensive error handling and logging
- 📝 Command usage tracking and analytics
- 🎭 Customizable bot presence and status
- 🔧 Guild-specific configuration support

🚀 **Developer Experience**
- 📦 Easy setup with Docker and docker-compose
- 🔒 Environment-based configuration with .env
- 📋 Type hints throughout the codebase
- 🧪 Ready for pytest integration
- 🎯 Slash commands and prefix commands support
- 🔌 Hot-reloadable extensions
- 📊 Database health monitoring

## Project Structure

```
DiscordPyBotTemplate/
├── bot/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bot.py              # Main bot class
│   │   └── config.py           # Configuration management
│   ├── cogs/
│   │   ├── __init__.py
│   │   ├── general.py          # General commands
│   │   └── admin.py            # Admin commands
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # Database models
│   │   └── manager.py          # Database manager
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging utilities
├── logs/                       # Log files (auto-created)
├── data/                       # Database files (auto-created)
├── .env.example                # Example environment variables
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── main.py                     # Entry point
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- A Discord bot token ([Create one here](https://discord.com/developers/applications))
- (Optional) PostgreSQL database
- (Optional) Docker and Docker Compose

### Installation

#### Option 1: Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd DiscordPyBotTemplate
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv

   # On Windows
   .venv\Scripts\activate

   # On Unix/MacOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and add your Discord bot token
   # Minimum required: DISCORD_TOKEN
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

#### Option 2: Docker Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd DiscordPyBotTemplate
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your configuration
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Start with SQLite (default)
   docker-compose up -d bot

   # Or start with PostgreSQL
   docker-compose up -d
   ```

4. **View logs**
   ```bash
   docker-compose logs -f bot
   ```

5. **Stop the bot**
   ```bash
   docker-compose down
   ```

## Configuration

### Environment Variables

Configure your bot by editing the `.env` file. Here are the most important settings:

#### Required Settings
```env
DISCORD_TOKEN=your_bot_token_here
```

#### Bot Settings
```env
DISCORD_PREFIX=!                    # Command prefix
BOT_NAME=MyDiscordBot              # Bot name for logging
BOT_VERSION=1.0.0                  # Bot version
ENVIRONMENT=development            # development, staging, production
```

#### Database Settings
```env
# SQLite (default)
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///data/bot.db

# PostgreSQL (uncomment to use)
# DATABASE_TYPE=postgresql
# POSTGRES_USER=botuser
# POSTGRES_PASSWORD=secure_password
# POSTGRES_DB=discord_bot
# POSTGRES_HOST=postgres
# POSTGRES_PORT=5432
```

#### Logging Settings
```env
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE=true
LOG_FILE_PATH=logs/bot.log
LOG_MAX_BYTES=10485760             # 10MB
LOG_BACKUP_COUNT=5
```

#### Feature Flags
```env
ENABLE_COMMAND_LOGGING=true        # Log command usage to database
ENABLE_ERROR_REPORTING=true        # Log errors to database
ENABLE_PRESENCE_UPDATE=true        # Update bot presence/status
```

#### Bot Presence
```env
PRESENCE_TYPE=playing              # playing, watching, listening, streaming
PRESENCE_TEXT=with commands | !help
PRESENCE_STATUS=online             # online, idle, dnd, invisible
```

See `.env.example` for all available configuration options.

## Usage

### Creating Custom Bots

You can use this template in two ways:

#### Method 1: Direct Usage
Simply modify the configuration and add your own cogs to the `bot/cogs/` directory.

#### Method 2: Subclassing
Create a custom bot by subclassing `DiscordBot`:

```python
from bot import DiscordBot, BotConfig

class MyCustomBot(DiscordBot):
    """Custom bot with additional features."""

    def __init__(self, config: BotConfig = None):
        super().__init__(config)
        # Add custom initialization here

    async def on_ready(self):
        """Override on_ready for custom behavior."""
        await super().on_ready()
        # Add custom ready logic here
        self.logger.info("Custom bot is ready!")

if __name__ == "__main__":
    config = BotConfig()
    bot = MyCustomBot(config)
    bot.run_bot()
```

### Creating Cogs

Create new cogs in the `bot/cogs/` directory. They will be automatically loaded on startup.

Example cog structure:

```python
from discord.ext import commands
from bot.core.bot import DiscordBot

class MyCog(commands.Cog):
    """My custom cog."""

    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.command(name="mycommand")
    async def my_command(self, ctx: commands.Context):
        """My custom command."""
        await ctx.send("Hello!")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Event listener example."""
        pass

async def setup(bot: DiscordBot):
    """Required setup function."""
    await bot.add_cog(MyCog(bot))
```

### Database Usage

The bot includes a powerful database manager that works with both SQLite and PostgreSQL.

#### Using Existing Models

```python
from bot.database.models import GuildConfig, UserData

# Get guild configuration
guild_config = await bot.db.get(GuildConfig, guild_id, "guild_id")

# Create user data
user = UserData(
    user_id=123456789,
    username="TestUser",
    experience=100,
    level=5
)
await bot.db.create(user)

# Update user data
user.experience += 50
await bot.db.update(user)
```

#### Creating Custom Models

```python
from datetime import datetime
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.models import Base

class MyModel(Base):
    """Custom database model."""

    __tablename__ = "my_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    data: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

### Admin Commands

The bot includes built-in admin commands (owner-only):

- `!sync` - Sync slash commands globally
- `!sync ~` - Sync slash commands to current guild
- `!reload <cog>` - Reload a cog
- `!load <cog>` - Load a cog
- `!unload <cog>` - Unload a cog
- `!cogs` - List all loaded cogs
- `!shutdown` - Shut down the bot
- `!dbhealth` - Check database health

### General Commands

Built-in commands available to all users:

- `!ping` or `/ping` - Check bot latency
- `!info` or `/info` - Display bot information
- `!serverinfo` - Display server information (guild only)

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format with black
black bot/

# Lint with ruff
ruff check bot/

# Type checking with mypy
mypy bot/
```

### Hot Reloading

While the bot is running, you can reload cogs without restarting:

```bash
!reload general  # Reloads the general cog
```

## Docker Deployment

### Building the Image

```bash
docker build -t discord-bot:latest .
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Restart bot
docker-compose restart bot

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production Considerations

1. **Use PostgreSQL in production** for better performance and reliability
2. **Set `ENVIRONMENT=production`** in your `.env` file
3. **Use strong passwords** for database credentials
4. **Enable log rotation** to prevent disk space issues
5. **Set up monitoring** for your bot's health
6. **Use Docker secrets** for sensitive data in production
7. **Regular backups** of your database

## Troubleshooting

### Common Issues

**Bot not starting:**
- Check that `DISCORD_TOKEN` is set correctly in `.env`
- Verify Python version is 3.11 or higher
- Check logs in the `logs/` directory

**Database errors:**
- Ensure the `data/` directory exists and is writable
- For PostgreSQL, verify connection details and that the database is running
- Check database health with `!dbhealth` command

**Commands not responding:**
- Verify bot has `MESSAGE_CONTENT` intent enabled in Discord Developer Portal
- Check bot has necessary permissions in the server
- Review command prefix in configuration

**Slash commands not appearing:**
- Run `!sync` to sync commands globally (takes up to 1 hour)
- Use `!sync ~` for instant sync in current guild (for testing)
- Verify bot has `applications.commands` scope

### Debug Mode

Enable debug mode for verbose logging:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation:** [discord.py docs](https://discordpy.readthedocs.io/)
- **Discord.py Server:** [discord.gg/dpy](https://discord.gg/dpy)
- **Issues:** [GitHub Issues](https://github.com/yourusername/DiscordPyBotTemplate/issues)

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Database management with [SQLAlchemy](https://www.sqlalchemy.org/)
- Configuration management with [Pydantic](https://docs.pydantic.dev/)
- Logging with [colorlog](https://github.com/borntyping/python-colorlog)

---

**Made with ❤️ for the Discord bot developer community**
