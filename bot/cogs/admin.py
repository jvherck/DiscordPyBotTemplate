"""
Admin commands cog.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

import discord
from discord import app_commands
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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Check if user has permission to use admin commands.

        Args:
            interaction: The interaction

        Returns:
            True if user is authorized
        """
        return await self.bot.is_owner(interaction.user)

    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync_prefix(self, ctx: commands.Context, spec: Optional[str] = None) -> None:
        """
        Sync slash commands (Prefix version).
        Usage: !sync [global|current|copy|clear]
        """
        await ctx.typing()

        if spec == "current":
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.reply(f"✅ Synced {len(synced)} commands to current guild")
        elif spec == "copy":
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.reply(f"✅ Copied and synced {len(synced)} commands to current guild")
        elif spec == "clear":
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.reply("✅ Cleared commands from current guild")
        else:
            synced = await self.bot.tree.sync()
            await ctx.reply(f"✅ Synced {len(synced)} commands globally")

    @commands.command(name="dbhealth", hidden=True)
    @commands.is_owner()
    async def dbhealth_prefix(self, ctx: commands.Context) -> None:
        """Check database connection health (Prefix version)."""
        if not self.bot.db:
            await ctx.reply("❌ Database not initialized")
            return

        is_healthy = await self.bot.db.health_check()
        if is_healthy:
            await ctx.reply("✅ Database connection is healthy")
        else:
            await ctx.reply("❌ Database connection is unhealthy")

    @app_commands.command(name="sync", description="Sync slash commands")
    @app_commands.describe(
        spec="Sync specification: global (default), current, copy, or clear"
    )
    @app_commands.choices(spec=[
        app_commands.Choice(name="Global", value="global"),
        app_commands.Choice(name="Current Guild", value="current"),
        app_commands.Choice(name="Copy Global to Guild", value="copy"),
        app_commands.Choice(name="Clear Guild", value="clear"),
    ])
    async def sync_commands(
            self,
            interaction: discord.Interaction,
            spec: Optional[app_commands.Choice[str]] = None,
    ) -> None:
        """
        Sync slash commands.

        Args:
            spec: Sync specification choice
        """
        await interaction.response.defer(ephemeral=True)

        spec_value = spec.value if spec else "global"

        if spec_value == "current":
            # Sync current guild
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(f"✅ Synced {len(synced)} commands to current guild")

        elif spec_value == "copy":
            # Copy global to current guild
            self.bot.tree.copy_global_to(guild=interaction.guild)
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                f"✅ Copied and synced {len(synced)} commands to current guild"
            )

        elif spec_value == "clear":
            # Clear current guild and sync
            self.bot.tree.clear_commands(guild=interaction.guild)
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send("✅ Cleared commands from current guild")

        else:
            # Global sync
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"✅ Synced {len(synced)} commands globally")

    @app_commands.command(name="reload", description="Reload a cog/extension")
    @app_commands.describe(extension="Name of the extension to reload")
    async def reload_extension(self, interaction: discord.Interaction, extension: str) -> None:
        """
        Reload a cog/extension.

        Args:
            extension: Name of the extension to reload
        """
        try:
            await self.bot.reload_extension(f"bot.cogs.{extension}")
            await interaction.response.send_message(f"✅ Reloaded extension: {extension}", ephemeral=True)
            self.bot.logger.info(f"Reloaded extension: {extension}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reload extension: {e}", ephemeral=True)
            self.bot.logger.error(f"Failed to reload extension {extension}: {e}")

    @app_commands.command(name="load", description="Load a cog/extension")
    @app_commands.describe(extension="Name of the extension to load")
    async def load_extension(self, interaction: discord.Interaction, extension: str) -> None:
        """
        Load a cog/extension.

        Args:
            extension: Name of the extension to load
        """
        try:
            await self.bot.load_extension(f"bot.cogs.{extension}")
            await interaction.response.send_message(f"✅ Loaded extension: {extension}", ephemeral=True)
            self.bot.logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to load extension: {e}", ephemeral=True)
            self.bot.logger.error(f"Failed to load extension {extension}: {e}")

    @app_commands.command(name="unload", description="Unload a cog/extension")
    @app_commands.describe(extension="Name of the extension to unload")
    async def unload_extension(self, interaction: discord.Interaction, extension: str) -> None:
        """
        Unload a cog/extension.

        Args:
            extension: Name of the extension to unload
        """
        try:
            await self.bot.unload_extension(f"bot.cogs.{extension}")
            await interaction.response.send_message(f"✅ Unloaded extension: {extension}", ephemeral=True)
            self.bot.logger.info(f"Unloaded extension: {extension}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unload extension: {e}", ephemeral=True)
            self.bot.logger.error(f"Failed to unload extension {extension}: {e}")

    @app_commands.command(name="cogs", description="List all loaded cogs")
    async def list_cogs(self, interaction: discord.Interaction) -> None:
        """List all loaded cogs."""
        cogs = [cog for cog in self.bot.cogs.keys()]

        if not cogs:
            await interaction.response.send_message("No cogs loaded.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Loaded Cogs",
            description="\n".join(f"• {cog}" for cog in sorted(cogs)),
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="shutdown", description="Shutdown the bot")
    async def shutdown_bot(self, interaction: discord.Interaction) -> None:
        """Shutdown the bot."""
        await interaction.response.send_message("👋 Shutting down...", ephemeral=True)
        self.bot.logger.info(f"Shutdown command issued by {interaction.user}")
        await self.bot.close()

    @app_commands.command(name="dbhealth", description="Check database connection health")
    async def database_health(self, interaction: discord.Interaction) -> None:
        """Check database connection health."""
        if not self.bot.db:
            await interaction.response.send_message("❌ Database not initialized", ephemeral=True)
            return

        is_healthy = await self.bot.db.health_check()
        if is_healthy:
            await interaction.response.send_message("✅ Database connection is healthy", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Database connection is unhealthy", ephemeral=True)


async def setup(bot: DiscordBot) -> None:
    """
    Load the Admin cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(Admin(bot))
