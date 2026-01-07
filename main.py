"""
Main entry point for the Discord bot.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

import sys

from bot import DiscordBot, BotConfig


def main() -> None:
    """Main function to start the bot."""
    # Load configuration
    config = BotConfig()

    # Create and run bot
    bot = DiscordBot(config=config)

    try:
        bot.run_bot()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
