"""
Configuration management using Pydantic settings.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .. import __version__


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PresenceType(str, Enum):
    """Bot presence types."""

    PLAYING = "playing"
    WATCHING = "watching"
    LISTENING = "listening"
    STREAMING = "streaming"


class PresenceStatus(str, Enum):
    """Bot status types."""

    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"


class DatabaseType(str, Enum):
    """Database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Discord Configuration
    discord_token: str = Field(..., description="Discord bot token")
    discord_prefix: str = Field(default="!", description="Command prefix")

    # Bot Settings
    bot_name: str = Field(default="MyDiscordBot", description="Bot name")
    bot_version: str = Field(default=__version__, description="Bot version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Environment")
    ignored_cogs: str = Field(default="", description="Comma-separated list of cogs to ignore")

    # Database Configuration
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE, description="Database type")
    database_url: str = Field(
        default="sqlite:///data/bot.db", description="Database connection URL"
    )

    # PostgreSQL specific
    postgres_user: str | None = Field(default=None, description="PostgreSQL username")
    postgres_password: str | None = Field(default=None, description="PostgreSQL password")
    postgres_db: str | None = Field(default=None, description="PostgreSQL database name")
    postgres_host: str = Field(default="postgres", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")

    # Logging Configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_file_path: str = Field(default="logs/bot.log", description="Log file path")
    log_max_bytes: int = Field(default=10485760, description="Max log file size (10MB)")
    log_backup_count: int = Field(default=5, description="Number of backup log files")

    # Feature Flags
    enable_command_logging: bool = Field(default=True, description="Enable command logging")
    enable_error_reporting: bool = Field(default=True, description="Enable error reporting")
    enable_presence_update: bool = Field(default=True, description="Enable presence updates")

    # Bot Presence
    presence_type: PresenceType = Field(
        default=PresenceType.PLAYING, description="Bot activity type"
    )
    presence_text: str = Field(
        default="with commands | !help", description="Bot activity text"
    )
    presence_status: PresenceStatus = Field(
        default=PresenceStatus.ONLINE, description="Bot status"
    )

    # Development Settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    dev_guild_id: int | None = Field(default=None, description="Development guild ID")

    # Rate Limiting
    command_cooldown: int = Field(default=3, description="Command cooldown in seconds")
    max_commands_per_minute: int = Field(
        default=20, description="Max commands per minute per user"
    )

    # Timezone
    timezone: str = Field(default="UTC", description="Bot timezone")

    @field_validator("database_url", mode="before")
    @classmethod
    def build_database_url(cls, v: str, info) -> str:
        """Build PostgreSQL URL if using PostgreSQL."""
        data = info.data
        if data.get("database_type") == DatabaseType.POSTGRESQL:
            if all(
                    [
                        data.get("postgres_user"),
                        data.get("postgres_password"),
                        data.get("postgres_db"),
                        data.get("postgres_host"),
                    ]
            ):
                return (
                    f"postgresql+asyncpg://{data['postgres_user']}:"
                    f"{data['postgres_password']}@{data['postgres_host']}:"
                    f"{data.get('postgres_port', 5432)}/{data['postgres_db']}"
                )
        return v

    @field_validator("log_file_path", mode="before")
    @classmethod
    def ensure_log_directory(cls, v: str) -> str:
        """Ensure log directory exists."""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.environment == Environment.STAGING

    def get_ignored_cogs_list(self) -> list[str]:
        """
        Get list of cogs to ignore on startup.

        Returns:
            List of cog names to ignore
        """
        if not self.ignored_cogs:
            return []
        return [cog.strip() for cog in self.ignored_cogs.split(",") if cog.strip()]

    def get_intents(self) -> dict[str, bool]:
        """Get Discord intents configuration."""
        return {
            "guilds": True,
            "members": True,
            "bans": True,
            "emojis": True,
            "integrations": True,
            "webhooks": True,
            "invites": True,
            "voice_states": True,
            "presences": False,  # Requires verification for bots in 100+ servers
            "messages": True,
            "reactions": True,
            "typing": False,
            "message_content": True,  # Required for prefix commands
        }
