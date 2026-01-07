"""
Template cog showing how to handle Discord events and messages.

This is a template file - copy and modify it to create your own event handler cogs.
To use this template, remove it from IGNORED_COGS in your .env file.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot.core.bot import DiscordBot


class TemplateEvents(commands.Cog):
    """Template cog demonstrating event listeners and message handling."""

    def __init__(self, bot: DiscordBot):
        """
        Initialize the template events cog.

        Args:
            bot: The bot instance
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listen for messages sent in channels the bot can see.

        This is an example of handling message events. You can use this to:
        - React to specific keywords
        - Implement custom message processing
        - Create message-based triggers

        Args:
            message: The message that was sent
        """
        # Ignore messages from bots (including ourselves)
        if message.author.bot:
            return

        # Example: React to messages containing "hello bot"
        if "hello bot" in message.content.lower():
            await message.add_reaction("👋")
            await message.channel.send(f"Hello {message.author.mention}!")

        # Example: Log messages starting with a specific prefix
        if message.content.startswith(">>log"):
            self.bot.logger.info(
                f"Special message from {message.author}: {message.content}"
            )

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        """
        Listen for message edits.

        Args:
            before: The message before editing
            after: The message after editing
        """
        # Ignore bot messages
        if before.author.bot:
            return

        # Example: Log message edits
        if before.content != after.content:
            self.bot.logger.debug(
                f"Message edited by {before.author} in {before.channel}: "
                f'"{before.content}" -> "{after.content}"'
            )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """
        Listen for message deletions.

        Args:
            message: The deleted message
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # Example: Log deleted messages
        self.bot.logger.debug(
            f"Message deleted by {message.author} in {message.channel}: "
            f'"{message.content}"'
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Listen for members joining the server.

        Args:
            member: The member who joined
        """
        self.bot.logger.info(f"{member} joined {member.guild.name}")

        # Example: Send a welcome message to a specific channel
        # Uncomment and modify as needed
        # welcome_channel = member.guild.system_channel
        # if welcome_channel:
        #     embed = discord.Embed(
        #         title="Welcome!",
        #         description=f"Welcome to the server, {member.mention}!",
        #         color=discord.Color.green(),
        #     )
        #     await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """
        Listen for members leaving the server.

        Args:
            member: The member who left
        """
        self.bot.logger.info(f"{member} left {member.guild.name}")

    @commands.Cog.listener()
    async def on_reaction_add(
        self, reaction: discord.Reaction, user: discord.User
    ) -> None:
        """
        Listen for reactions being added to messages.

        Args:
            reaction: The reaction that was added
            user: The user who added the reaction
        """
        # Ignore bot reactions
        if user.bot:
            return

        # Example: Log specific emoji reactions
        if str(reaction.emoji) == "⭐":
            self.bot.logger.info(
                f"{user} starred a message in {reaction.message.channel}"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """
        Listen for voice state changes (joining/leaving voice channels).

        Args:
            member: The member whose voice state changed
            before: The voice state before the change
            after: The voice state after the change
        """
        # Example: Log when members join/leave voice channels
        if before.channel is None and after.channel is not None:
            # Member joined a voice channel
            self.bot.logger.debug(f"{member} joined voice channel: {after.channel.name}")
        elif before.channel is not None and after.channel is None:
            # Member left a voice channel
            self.bot.logger.debug(f"{member} left voice channel: {before.channel.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Listen for reactions (even on uncached messages).

        This is useful for reaction roles or other features that need to work
        with older messages that might not be in cache.

        Args:
            payload: The raw reaction event payload
        """
        # Example: Implement a simple reaction role system
        # Uncomment and modify as needed
        #
        # if payload.message_id == YOUR_MESSAGE_ID:
        #     guild = self.bot.get_guild(payload.guild_id)
        #     if guild:
        #         role = guild.get_role(YOUR_ROLE_ID)
        #         member = guild.get_member(payload.user_id)
        #         if role and member and not member.bot:
        #             await member.add_roles(role)
        pass


async def setup(bot: DiscordBot) -> None:
    """
    Load the TemplateEvents cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(TemplateEvents(bot))
