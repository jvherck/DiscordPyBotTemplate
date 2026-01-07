"""
Example of creating a custom cog with various command types.

This demonstrates:
- Prefix commands
- Slash commands
- Command groups
- Cooldowns and checks
- Error handling
- Database interaction
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot.core.bot import DiscordBot


class ExampleCog(commands.Cog):
    """Example cog with various command types and features."""

    def __init__(self, bot: DiscordBot):
        """
        Initialize the Example cog.

        Args:
            bot: The bot instance
        """
        self.bot = bot

    # Basic prefix command
    @commands.command(name="hello", aliases=["hi", "greet"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hello_command(self, ctx: commands.Context, name: Optional[str] = None) -> None:
        """
        Say hello to someone.

        Args:
            name: Optional name to greet
        """
        greeting = f"Hello, {name}!" if name else f"Hello, {ctx.author.mention}!"
        await ctx.send(greeting)

    # Slash command
    @app_commands.command(name="hello", description="Say hello to someone")
    @app_commands.describe(name="The name to greet")
    async def hello_slash(
            self, interaction: discord.Interaction, name: Optional[str] = None
    ) -> None:
        """
        Slash command version of hello.

        Args:
            interaction: Discord interaction
            name: Optional name to greet
        """
        greeting = f"Hello, {name}!" if name else f"Hello, {interaction.user.mention}!"
        await interaction.response.send_message(greeting)

    # Command with database interaction
    @commands.command(name="profile", aliases=["me", "stats"])
    async def profile_command(self, ctx: commands.Context) -> None:
        """Display user profile from database."""
        if not self.bot.db:
            await ctx.send("❌ Database not available")
            return

        try:
            from bot.database.models import UserData

            # Get or create user data
            user_data = await self.bot.db.get(UserData, ctx.author.id, "user_id")

            if not user_data:
                # Create new user
                user_data = UserData(
                    user_id=ctx.author.id,
                    username=str(ctx.author),
                    experience=0,
                    level=1,
                    coins=100,  # Starting coins
                )
                await self.bot.db.create(user_data)

            embed = discord.Embed(
                title=f"{ctx.author.name}'s Profile",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Level", value=user_data.level, inline=True)
            embed.add_field(name="Experience", value=user_data.experience, inline=True)
            embed.add_field(name="Coins", value=f"💰 {user_data.coins}", inline=True)

            if user_data.last_daily:
                embed.add_field(
                    name="Last Daily",
                    value=discord.utils.format_dt(user_data.last_daily, style="R"),
                    inline=False,
                )

            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)

            await ctx.send(embed=embed)

        except Exception as e:
            self.bot.logger.error(f"Error fetching profile: {e}")
            await ctx.send("❌ Error fetching profile")

    # Command with cooldown and database update
    @commands.command(name="daily")
    @commands.cooldown(1, 86400, commands.BucketType.user)  # Once per day
    async def daily_command(self, ctx: commands.Context) -> None:
        """Claim daily coins."""
        if not self.bot.db:
            await ctx.send("❌ Database not available")
            return

        try:
            from bot.database.models import UserData

            user_data = await self.bot.db.get(UserData, ctx.author.id, "user_id")

            if not user_data:
                user_data = UserData(
                    user_id=ctx.author.id,
                    username=str(ctx.author),
                )
                await self.bot.db.create(user_data)

            # Check if already claimed today
            if user_data.last_daily:
                time_since_daily = datetime.utcnow() - user_data.last_daily
                if time_since_daily < timedelta(days=1):
                    time_left = timedelta(days=1) - time_since_daily
                    hours = time_left.seconds // 3600
                    minutes = (time_left.seconds % 3600) // 60
                    await ctx.send(
                        f"⏰ You already claimed your daily! "
                        f"Come back in {hours}h {minutes}m"
                    )
                    return

            # Give coins
            daily_amount = 100
            user_data.coins += daily_amount
            user_data.last_daily = datetime.utcnow()
            await self.bot.db.update(user_data)

            await ctx.send(f"💰 You claimed {daily_amount} coins! Total: {user_data.coins}")

        except Exception as e:
            self.bot.logger.error(f"Error claiming daily: {e}")
            await ctx.send("❌ Error claiming daily coins")

    # Command group
    @commands.group(name="admin", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def admin_group(self, ctx: commands.Context) -> None:
        """Admin command group."""
        await ctx.send("Use `!admin <subcommand>`. Available: clear, config")

    @admin_group.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def admin_clear(self, ctx: commands.Context, amount: int = 10) -> None:
        """
        Clear messages in the channel.

        Args:
            amount: Number of messages to clear (default: 10)
        """
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1 and 100")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for the command itself
        await ctx.send(f"✅ Deleted {len(deleted) - 1} messages", delete_after=5)

    @admin_group.command(name="config")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def admin_config(self, ctx: commands.Context, key: str, value: str) -> None:
        """
        Update guild configuration.

        Args:
            key: Configuration key
            value: Configuration value
        """
        if not self.bot.db:
            await ctx.send("❌ Database not available")
            return

        try:
            from bot.database.models import GuildConfig

            guild_config = await self.bot.db.get(
                GuildConfig, ctx.guild.id, "guild_id"
            )

            if not guild_config:
                guild_config = GuildConfig(guild_id=ctx.guild.id)
                await self.bot.db.create(guild_config)

            # Update configuration
            if key == "prefix":
                guild_config.prefix = value
            elif key == "language":
                guild_config.language = value
            else:
                await ctx.send(f"❌ Unknown config key: {key}")
                return

            await self.bot.db.update(guild_config)
            await ctx.send(f"✅ Updated {key} to {value}")

        except Exception as e:
            self.bot.logger.error(f"Error updating config: {e}")
            await ctx.send("❌ Error updating configuration")

    # Event listener
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Example message listener.

        Args:
            message: Discord message
        """
        # Don't respond to bots
        if message.author.bot:
            return

        # Example: Give XP for messages
        if self.bot.db and message.guild:
            try:
                from bot.database.models import UserData

                user_data = await self.bot.db.get(
                    UserData, message.author.id, "user_id"
                )

                if user_data:
                    # Add XP (1-5 per message)
                    user_data.experience += 1

                    # Level up check
                    xp_needed = 100 * (user_data.level ** 1.5)
                    if user_data.experience >= xp_needed:
                        user_data.level += 1
                        await message.channel.send(
                            f"🎉 {message.author.mention} leveled up to level {user_data.level}!"
                        )

                    await self.bot.db.update(user_data)

            except Exception as e:
                self.bot.logger.error(f"Error updating XP: {e}")

    # Error handler for this cog
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """
        Handle errors for commands in this cog.

        Args:
            ctx: Command context
            error: The error that occurred
        """
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s"
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ You need these permissions: {', '.join(error.missing_permissions)}")


async def setup(bot: DiscordBot) -> None:
    """
    Load the Example cog.

    Args:
        bot: The bot instance
    """
    await bot.add_cog(ExampleCog(bot))
