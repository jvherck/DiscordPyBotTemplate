"""
General commands cog.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

import platform
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot.core.bot import DiscordBot


class General(commands.Cog):
    """General purpose commands."""

    def __init__(self, bot: DiscordBot):
        """
        Initialize the General cog.

        Args:
            bot: The bot instance
        """
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

    @app_commands.command(name="info", description="Display bot information")
    async def info(self, interaction: discord.Interaction) -> None:
        """Display bot information."""
        embed = discord.Embed(
            title=f"{self.bot.config.bot_name} Information",
            color=discord.Color.blue(),
            description=f"A professional Discord bot built with discord.py {discord.__version__}",
        )

        embed.add_field(name="Version", value=self.bot.config.bot_version, inline=True)
        embed.add_field(
            name="Environment", value=self.bot.config.environment.value, inline=True
        )
        embed.add_field(name="Prefix", value=self.bot.config.discord_prefix, inline=True)

        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Commands", value=len(self.bot.commands), inline=True
        )

        if self.bot.uptime:
            hours, remainder = divmod(int(self.bot.uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours}h {minutes}m {seconds}s"
            embed.add_field(name="Uptime", value=uptime_str, inline=True)

        embed.add_field(
            name="Python", value=platform.python_version(), inline=True
        )
        embed.add_field(
            name="Platform",
            value=f"{platform.system()} {platform.release()}",
            inline=True,
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None,
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Display server information")
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        """Display server information."""
        guild = interaction.guild

        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.blue(),
            description=guild.description or "No description set",
        )

        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(guild.created_at, style="R"),
            inline=True,
        )

        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)

        embed.add_field(
            name="Boost Level", value=f"Level {guild.premium_tier}", inline=True
        )
        embed.add_field(
            name="Boosts", value=guild.premium_subscription_count or 0, inline=True
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Handle bot joining a new guild."""
        self.bot.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")

        # Create default guild config
        if self.bot.db:
            try:
                from bot.database.models import GuildConfig

                guild_config = GuildConfig(
                    guild_id=guild.id,
                    prefix=self.bot.config.discord_prefix,
                )
                await self.bot.db.create(guild_config)
                self.bot.logger.info(f"Created config for guild {guild.id}")
            except Exception as e:
                self.bot.logger.error(f"Failed to create guild config: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Handle bot leaving a guild."""
        self.bot.logger.info(f"Left guild: {guild.name} (ID: {guild.id})")


async def setup(bot: DiscordBot) -> None:
    """
    Load the General cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(General(bot))
