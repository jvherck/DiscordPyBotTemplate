"""Development runner script with auto-reload capabilities."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run the bot in development mode with helpful output."""
    print("🚀 Starting Discord Bot in Development Mode")
    print("=" * 50)

    try:
        from bot import DiscordBot, BotConfig

        # Load configuration
        config = BotConfig()

        # Override some settings for development
        config.environment = BotConfig.environment.DEVELOPMENT
        config.log_level = BotConfig.log_level.DEBUG
        config.debug_mode = True

        print(f"Bot Name: {config.bot_name}")
        print(f"Prefix: {config.discord_prefix}")
        print(f"Database: {config.database_type.value}")
        print(f"Log Level: {config.log_level.value}")
        print("=" * 50)
        print("\n💡 Tip: Use !reload <cog> to reload cogs without restarting")
        print("💡 Tip: Press Ctrl+C to stop the bot\n")

        # Create and run bot
        bot = DiscordBot(config=config)
        asyncio.run(bot.start())

    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
