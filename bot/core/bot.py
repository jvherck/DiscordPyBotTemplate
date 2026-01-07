"""
Core Discord bot implementation.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

import asyncio
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Optional

import discord
from discord.ext import commands

from bot.core.config import BotConfig, PresenceStatus, PresenceType
from bot.database.manager import DatabaseManager
from bot.database.models import CommandLog, ErrorLog
from bot.utils.logger import setup_discord_logging, setup_logger


class DiscordBot(commands.Bot):
    """
    Main Discord bot class with enterprise-level features.

    This class extends discord.ext.commands.Bot with:
    - Configuration management
    - Database integration
    - Advanced logging
    - Error tracking
    - Command usage logging
    - Automatic cog loading
    - Presence management
    """

    def __init__(
            self,
            config: Optional[BotConfig] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        Initialize the Discord bot.

        Args:
            config: Bot configuration (loads from .env if not provided)
            *args: Additional arguments for commands.Bot
            **kwargs: Additional keyword arguments for commands.Bot
        """
        # Load configuration
        self.config = config or BotConfig()

        # Set up intents
        intents = discord.Intents(**self.config.get_intents())

        # Initialize logger
        self.logger = setup_logger(self.config.bot_name, self.config)
        setup_discord_logging(self.config)

        # Initialize parent Bot class
        super().__init__(
            command_prefix=self._get_prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
            *args,
            **kwargs,
        )

        # Initialize components
        self.db: Optional[DatabaseManager] = None
        self.start_time: Optional[float] = None
        self._is_ready = False

        self.logger.info(f"Initializing {self.config.bot_name} v{self.config.bot_version}")
        self.logger.info(f"Environment: {self.config.environment.value}")

    async def _get_prefix(
            self, bot: DiscordBot, message: discord.Message
    ) -> list[str]:
        """
        Get command prefix for a guild.

        Args:
            bot: Bot instance
            message: Discord message

        Returns:
            List of valid prefixes
        """
        prefixes = [self.config.discord_prefix]

        # Check for guild-specific prefix
        if message.guild and self.db:
            try:
                from bot.database.models import GuildConfig

                guild_config = await self.db.get(
                    GuildConfig, message.guild.id, "guild_id"
                )
                if guild_config and guild_config.prefix:
                    prefixes.insert(0, guild_config.prefix)
            except Exception as e:
                self.logger.error(f"Error fetching guild prefix: {e}")

        return commands.when_mentioned_or(*prefixes)(bot, message)

    async def setup_hook(self) -> None:
        """
        Async setup hook called before the bot starts.

        This is where we initialize database, load cogs, and perform
        other async setup operations.
        """
        self.logger.info("Running setup hook...")

        # Initialize database
        await self._initialize_database()

        # Load extensions/cogs
        await self._load_extensions()

        # Set up command error handler
        self.tree.error(self._on_app_command_error)

        self.logger.info("Setup hook completed")

    async def _initialize_database(self) -> None:
        """Initialize database connection."""
        try:
            self.db = DatabaseManager(self.config, self.logger)
            await self.db.initialize()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.critical(f"Failed to initialize database: {e}")
            self.logger.critical(traceback.format_exc())
            raise

    async def _load_extensions(self) -> None:
        """Load all extension cogs from the cogs directory."""
        cogs_dir = Path("bot/cogs")
        if not cogs_dir.exists():
            self.logger.warning(f"Cogs directory not found: {cogs_dir}")
            return

        # Get list of cogs to ignore
        ignored_cogs = self.config.get_ignored_cogs_list()
        if ignored_cogs:
            self.logger.info(f"Ignoring cogs: {', '.join(ignored_cogs)}")

        loaded = 0
        failed = 0

        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue

            # Check if this cog should be ignored
            if cog_file.stem in ignored_cogs:
                self.logger.info(f"Skipping ignored cog: {cog_file.stem}")
                continue

            cog_name = f"bot.cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                self.logger.info(f"Loaded extension: {cog_name}")
                loaded += 1
            except Exception as e:
                self.logger.error(f"Failed to load extension {cog_name}: {e}")
                self.logger.error(traceback.format_exc())
                failed += 1

        self.logger.info(
            f"Extension loading complete: {loaded} loaded, {failed} failed"
        )

    async def on_ready(self) -> None:
        """Called when the bot is ready and connected to Discord."""
        if self._is_ready:
            self.logger.info("Bot reconnected")
            return

        self._is_ready = True
        self.start_time = time.time()

        self.logger.info("=" * 50)
        self.logger.info(f"Bot is ready!")
        self.logger.info(f"Logged in as: {self.user.name} (ID: {self.user.id})")
        self.logger.info(f"Discord.py version: {discord.__version__}")
        self.logger.info(f"Python version: {sys.version.split()[0]}")
        self.logger.info(f"Guilds: {len(self.guilds)}")
        self.logger.info(f"Users: {len(self.users)}")
        self.logger.info("=" * 50)

        # Set presence
        if self.config.enable_presence_update:
            await self._set_presence()

        # Sync slash commands in dev mode
        if self.config.debug_mode and self.config.dev_guild_id:
            try:
                guild = discord.Object(id=self.config.dev_guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                self.logger.info(f"Synced commands to dev guild {self.config.dev_guild_id}")
            except Exception as e:
                self.logger.error(f"Failed to sync dev guild commands: {e}")

    async def _set_presence(self) -> None:
        """Set bot presence/status."""
        try:
            activity_type_map = {
                PresenceType.PLAYING: discord.ActivityType.playing,
                PresenceType.WATCHING: discord.ActivityType.watching,
                PresenceType.LISTENING: discord.ActivityType.listening,
                PresenceType.STREAMING: discord.ActivityType.streaming,
            }

            status_map = {
                PresenceStatus.ONLINE: discord.Status.online,
                PresenceStatus.IDLE: discord.Status.idle,
                PresenceStatus.DND: discord.Status.dnd,
                PresenceStatus.INVISIBLE: discord.Status.invisible,
            }

            activity = discord.Activity(
                type=activity_type_map[self.config.presence_type],
                name=self.config.presence_text,
            )

            await self.change_presence(
                activity=activity, status=status_map[self.config.presence_status]
            )

            self.logger.info(
                f"Presence set: {self.config.presence_type.value} "
                f"{self.config.presence_text}"
            )
        except Exception as e:
            self.logger.error(f"Failed to set presence: {e}")

    async def on_command(self, ctx: commands.Context) -> None:
        """
        Called when a command is invoked.

        Args:
            ctx: Command context
        """
        if self.config.enable_command_logging:
            self.logger.info(
                f"Command '{ctx.command.name}' invoked by {ctx.author} "
                f"in {ctx.guild.name if ctx.guild else 'DM'}"
            )

    async def on_command_completion(self, ctx: commands.Context) -> None:
        """
        Called when a command completes successfully.

        Args:
            ctx: Command context
        """
        if self.config.enable_command_logging and self.db:
            await self._log_command(ctx, success=True)

    async def on_command_error(
            self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """
        Global command error handler.

        Args:
            ctx: Command context
            error: The error that occurred
        """
        # Log to database
        if self.config.enable_error_reporting and self.db:
            await self._log_command(ctx, success=False, error=error)
            await self._log_error(error, ctx=ctx)

        # Handle specific errors
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                f"❌ You don't have permission to use this command. "
                f"Required: {', '.join(error.missing_permissions)}"
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                f"❌ I don't have the required permissions. "
                f"Missing: {', '.join(error.missing_permissions)}"
            )
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ This command is on cooldown. "
                f"Try again in {error.retry_after:.1f} seconds."
            )
            return

        # Log unexpected errors
        self.logger.error(
            f"Command error in {ctx.command}: {error}", exc_info=error
        )
        await ctx.send(
            "❌ An unexpected error occurred while executing the command."
        )

    async def _on_app_command_error(
            self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError
    ) -> None:
        """
        Global app command (slash command) error handler.

        Args:
            interaction: Discord interaction
            error: The error that occurred
        """
        if self.config.enable_error_reporting and self.db:
            await self._log_error(error, interaction=interaction)

        self.logger.error(f"App command error: {error}", exc_info=error)

        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True,
                )
        except Exception:
            pass

    async def _log_command(
            self,
            ctx: commands.Context,
            success: bool = True,
            error: Optional[Exception] = None,
    ) -> None:
        """
        Log command usage to database.

        Args:
            ctx: Command context
            success: Whether command executed successfully
            error: Optional error if command failed
        """
        try:
            command_log = CommandLog(
                guild_id=ctx.guild.id if ctx.guild else None,
                channel_id=ctx.channel.id,
                user_id=ctx.author.id,
                command_name=ctx.command.qualified_name if ctx.command else "unknown",
                command_args=ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
                if ctx.invoked_with
                else None,
                is_slash_command=False,
                success=success,
                error_message=str(error) if error else None,
            )
            await self.db.create(command_log)
        except Exception as e:
            self.logger.error(f"Failed to log command: {e}")

    async def _log_error(
            self,
            error: Exception,
            ctx: Optional[commands.Context] = None,
            interaction: Optional[discord.Interaction] = None,
    ) -> None:
        """
        Log error to database.

        Args:
            error: The error that occurred
            ctx: Optional command context
            interaction: Optional interaction
        """
        try:
            error_log = ErrorLog(
                guild_id=(
                    ctx.guild.id
                    if ctx and ctx.guild
                    else interaction.guild_id
                    if interaction
                    else None
                ),
                channel_id=(
                    ctx.channel.id
                    if ctx
                    else interaction.channel_id
                    if interaction
                    else None
                ),
                user_id=(
                    ctx.author.id
                    if ctx
                    else interaction.user.id
                    if interaction
                    else None
                ),
                command_name=(
                    ctx.command.qualified_name
                    if ctx and ctx.command
                    else interaction.command.name
                    if interaction and interaction.command
                    else None
                ),
                error_type=type(error).__name__,
                error_message=str(error),
                traceback="".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                ),
            )
            await self.db.create(error_log)
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}")

    async def close(self) -> None:
        """Close bot and cleanup resources."""
        self.logger.info("Shutting down bot...")

        # Close database connection
        if self.db:
            await self.db.close()

        # Close bot connection
        await super().close()

        self.logger.info("Bot shutdown complete")

    async def start(self, token: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        """
        Start the bot.

        Args:
            token: Discord bot token (uses config if not provided)
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        token = token or self.config.discord_token
        await super().start(token, *args, **kwargs)

    def run_bot(self, token: Optional[str] = None) -> None:
        """
        Run the bot (blocking).

        Args:
            token: Discord bot token (uses config if not provided)
        """
        token = token or self.config.discord_token

        try:
            asyncio.run(self.start(token))
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.critical(f"Fatal error: {e}")
            self.logger.critical(traceback.format_exc())
            raise

    @property
    def uptime(self) -> Optional[float]:
        """
        Get bot uptime in seconds.

        Returns:
            Uptime in seconds or None if not started
        """
        if self.start_time:
            return time.time() - self.start_time
        return None
