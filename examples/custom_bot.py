"""
Example of creating a custom bot by subclassing DiscordBot.

This demonstrates how to extend the base bot with custom functionality
while keeping all the enterprise features intact.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import discord
from discord.ext import tasks

from bot import DiscordBot, BotConfig


class MyCustomBot(DiscordBot):
    """
    Custom Discord bot with additional features.

    Extends the base DiscordBot with custom initialization,
    event handlers, and background tasks.
    """

    def __init__(self, config: BotConfig | None = None):
        """
        Initialize the custom bot.

        Args:
            config: Bot configuration (loads from .env if not provided)
        """
        super().__init__(config)

        # Custom bot attributes
        self.custom_data = {}
        self.message_count = 0

        self.logger.info("Custom bot initialized with additional features")

    async def setup_hook(self) -> None:
        """
        Extended setup hook with custom initialization.

        This runs before the bot starts and is where you should
        initialize custom services, APIs, etc.
        """
        # Call parent setup
        await super().setup_hook()

        # Custom setup logic
        self.logger.info("Running custom setup logic...")

        # Example: Initialize custom service
        await self._init_custom_service()

        # Start background tasks
        self.status_updater.start()

        self.logger.info("Custom setup completed")

    async def _init_custom_service(self) -> None:
        """Initialize custom service (example)."""
        # This is where you'd initialize external APIs, services, etc.
        self.custom_data["initialized"] = True
        self.logger.info("Custom service initialized")

    async def on_ready(self) -> None:
        """
        Extended on_ready event.

        Called when the bot is ready and connected to Discord.
        """
        # Call parent on_ready
        await super().on_ready()

        # Custom ready logic
        self.logger.info("=" * 50)
        self.logger.info("Custom Bot Features:")
        self.logger.info(f"- Custom Data: {self.custom_data}")
        self.logger.info(f"- Background Tasks Running: {self.status_updater.is_running()}")
        self.logger.info("=" * 50)

    async def on_message(self, message: discord.Message) -> None:
        """
        Custom message handler.

        Args:
            message: Discord message
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # Increment message counter
        self.message_count += 1

        # Log every 100th message
        if self.message_count % 100 == 0:
            self.logger.info(f"Processed {self.message_count} messages")

        # Process commands (important!)
        await self.process_commands(message)

    async def on_member_join(self, member: discord.Member) -> None:
        """
        Handle member join events.

        Args:
            member: The member who joined
        """
        self.logger.info(f"New member joined: {member.name} in {member.guild.name}")

        # Example: Send welcome message
        if self.db:
            try:
                from bot.database.models import GuildConfig

                guild_config = await self.db.get(
                    GuildConfig, member.guild.id, "guild_id"
                )

                if guild_config and guild_config.welcome_channel_id:
                    channel = member.guild.get_channel(guild_config.welcome_channel_id)
                    if channel:
                        await channel.send(
                            f"👋 Welcome to {member.guild.name}, {member.mention}!"
                        )
            except Exception as e:
                self.logger.error(f"Error sending welcome message: {e}")

    @tasks.loop(minutes=30)
    async def status_updater(self) -> None:
        """
        Background task that updates bot status every 30 minutes.

        This is an example of a custom background task.
        """
        try:
            # Update status with message count
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | {self.message_count} messages",
            )
            await self.change_presence(activity=activity, status=discord.Status.online)

            self.logger.debug("Status updated by background task")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    @status_updater.before_loop
    async def before_status_updater(self) -> None:
        """Wait for bot to be ready before starting the status updater."""
        await self.wait_until_ready()

    async def close(self) -> None:
        """
        Extended close method with cleanup.

        This is called when the bot is shutting down.
        """
        self.logger.info("Running custom cleanup...")

        # Stop background tasks
        if self.status_updater.is_running():
            self.status_updater.cancel()

        # Custom cleanup logic
        self.custom_data.clear()

        # Call parent close
        await super().close()

        self.logger.info("Custom cleanup completed")


def main() -> None:
    """Main function to start the custom bot."""
    # Load configuration
    config = BotConfig()

    # Create custom bot instance
    bot = MyCustomBot(config=config)

    # Run the bot
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
