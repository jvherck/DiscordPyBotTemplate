"""
Template cog showing how to create slash commands.

This is a template file - copy and modify it to create your own slash command cogs.
To use this template, remove it from IGNORED_COGS in your .env file.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot.core.bot import DiscordBot


class TemplateSlash(commands.Cog):
    """Template cog demonstrating slash commands."""

    def __init__(self, bot: DiscordBot):
        """
        Initialize the template slash cog.

        Args:
            bot: The bot instance
        """
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to someone")
    @app_commands.describe(user="The user to greet (optional)")
    async def hello(
        self, interaction: discord.Interaction, user: discord.User | None = None
    ) -> None:
        """
        A simple slash command that greets a user.

        Args:
            interaction: The interaction
            user: Optional user to greet
        """
        target = user or interaction.user
        await interaction.response.send_message(f"👋 Hello, {target.mention}!")

    @app_commands.command(name="embed", description="Send a fancy embed message")
    @app_commands.describe(
        title="The title of the embed",
        description="The description of the embed",
        color="Hex color code (e.g., #FF5733)",
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: str | None = None,
    ) -> None:
        """
        Create and send an embed.

        Args:
            interaction: The interaction
            title: Embed title
            description: Embed description
            color: Optional hex color code
        """
        # Parse color if provided
        embed_color = discord.Color.blue()
        if color:
            try:
                # Remove # if present
                color = color.lstrip("#")
                embed_color = discord.Color(int(color, 16))
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid color code. Use hex format like #FF5733", ephemeral=True
                )
                return

        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(
            text=f"Created by {interaction.user}",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None,
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choice", description="Make a choice from options")
    @app_commands.describe(option="Choose an option")
    @app_commands.choices(
        option=[
            app_commands.Choice(name="Option 1", value="opt1"),
            app_commands.Choice(name="Option 2", value="opt2"),
            app_commands.Choice(name="Option 3", value="opt3"),
        ]
    )
    async def choice(
        self, interaction: discord.Interaction, option: app_commands.Choice[str]
    ) -> None:
        """
        Demonstrate how to use choices in slash commands.

        Args:
            interaction: The interaction
            option: The selected choice
        """
        await interaction.response.send_message(
            f"You selected: **{option.name}** (value: `{option.value}`)"
        )

    # Example of a command group
    group = app_commands.Group(
        name="example", description="Example command group"
    )

    @group.command(name="subcommand", description="An example subcommand")
    @app_commands.describe(text="Some text to echo")
    async def subcommand(self, interaction: discord.Interaction, text: str) -> None:
        """
        Example subcommand within a group.

        Args:
            interaction: The interaction
            text: Text to echo back
        """
        await interaction.response.send_message(f"You said: {text}")

    @group.command(name="info", description="Show info about this group")
    async def group_info(self, interaction: discord.Interaction) -> None:
        """
        Show information about command groups.

        Args:
            interaction: The interaction
        """
        embed = discord.Embed(
            title="Command Groups",
            description=(
                "This is an example of a command group. "
                "Groups allow you to organize related commands together.\n\n"
                "Usage: `/example subcommand` or `/example info`"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: DiscordBot) -> None:
    """
    Load the TemplateSlash cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(TemplateSlash(bot))
