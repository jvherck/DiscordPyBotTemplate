"""Admin commands cog."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot.core.bot import DiscordBot


class Admin(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot: DiscordBot):
        """
        Initialize the Admin cog.

        Args:
            bot: The bot instance
        """
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        """
        Check if user has permission to use admin commands.

        Args:
            ctx: Command context

        Returns:
            True if user is authorized
        """
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="sync")
    async def sync_commands(
            self,
            ctx: commands.Context,
            guild_id: Optional[int] = None,
            spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """
        Sync slash commands.

        Args:
            guild_id: Optional guild ID to sync to
            spec: Sync specification
                ~ - sync current guild
                * - copy global to current guild
                ^ - clear current guild and sync
        """
        if spec == "~":
            # Sync current guild
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ Synced {len(synced)} commands to current guild")

        elif spec == "*":
            # Copy global to current guild
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                f"✅ Copied and synced {len(synced)} commands to current guild"
            )

        elif spec == "^":
            # Clear current guild and sync
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send("✅ Cleared commands from current guild")

        elif guild_id:
            # Sync to specific guild
            guild = discord.Object(id=guild_id)
            synced = await self.bot.tree.sync(guild=guild)
            await ctx.send(f"✅ Synced {len(synced)} commands to guild {guild_id}")

        else:
            # Global sync
            synced = await self.bot.tree.sync()
            await ctx.send(f"✅ Synced {len(synced)} commands globally")

    @commands.command(name="reload")
    async def reload_extension(self, ctx: commands.Context, extension: str) -> None:
        """
        Reload a cog/extension.

        Args:
            extension: Name of the extension to reload
        """
        try:
            await self.bot.reload_extension(f"bot.cogs.{extension}")
            await ctx.send(f"✅ Reloaded extension: {extension}")
            self.bot.logger.info(f"Reloaded extension: {extension}")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload extension: {e}")
            self.bot.logger.error(f"Failed to reload extension {extension}: {e}")

    @commands.command(name="load")
    async def load_extension(self, ctx: commands.Context, extension: str) -> None:
        """
        Load a cog/extension.

        Args:
            extension: Name of the extension to load
        """
        try:
            await self.bot.load_extension(f"bot.cogs.{extension}")
            await ctx.send(f"✅ Loaded extension: {extension}")
            self.bot.logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            await ctx.send(f"❌ Failed to load extension: {e}")
            self.bot.logger.error(f"Failed to load extension {extension}: {e}")

    @commands.command(name="unload")
    async def unload_extension(self, ctx: commands.Context, extension: str) -> None:
        """
        Unload a cog/extension.

        Args:
            extension: Name of the extension to unload
        """
        try:
            await self.bot.unload_extension(f"bot.cogs.{extension}")
            await ctx.send(f"✅ Unloaded extension: {extension}")
            self.bot.logger.info(f"Unloaded extension: {extension}")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload extension: {e}")
            self.bot.logger.error(f"Failed to unload extension {extension}: {e}")

    @commands.command(name="cogs")
    async def list_cogs(self, ctx: commands.Context) -> None:
        """List all loaded cogs."""
        cogs = [cog for cog in self.bot.cogs.keys()]

        if not cogs:
            await ctx.send("No cogs loaded.")
            return

        embed = discord.Embed(
            title="Loaded Cogs",
            description="\n".join(f"• {cog}" for cog in sorted(cogs)),
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="shutdown")
    async def shutdown_bot(self, ctx: commands.Context) -> None:
        """Shutdown the bot."""
        await ctx.send("👋 Shutting down...")
        self.bot.logger.info(f"Shutdown command issued by {ctx.author}")
        await self.bot.close()

    @commands.command(name="dbhealth")
    async def database_health(self, ctx: commands.Context) -> None:
        """Check database connection health."""
        if not self.bot.db:
            await ctx.send("❌ Database not initialized")
            return

        is_healthy = await self.bot.db.health_check()
        if is_healthy:
            await ctx.send("✅ Database connection is healthy")
        else:
            await ctx.send("❌ Database connection is unhealthy")


async def setup(bot: DiscordBot) -> None:
    """
    Load the Admin cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(Admin(bot))
