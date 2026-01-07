"""
Database models using SQLAlchemy.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class GuildConfig(Base):
    """Guild-specific configuration."""

    __tablename__ = "guild_config"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    prefix: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    welcome_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    log_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    auto_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    command_logging_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<GuildConfig(guild_id={self.guild_id}, prefix={self.prefix})>"


class CommandLog(Base):
    """Command usage logging."""

    __tablename__ = "command_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(BigInteger)
    command_name: Mapped[str] = mapped_column(String(100))
    command_args: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_slash_command: Mapped[bool] = mapped_column(Boolean, default=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<CommandLog(id={self.id}, command={self.command_name}, "
            f"user_id={self.user_id}, success={self.success})>"
        )


class ErrorLog(Base):
    """Error logging."""

    __tablename__ = "error_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    command_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_type: Mapped[str] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(Text)
    traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ErrorLog(id={self.id}, error_type={self.error_type}, "
            f"command={self.command_name})>"
        )


class UserData(Base):
    """User-specific data (example model)."""

    __tablename__ = "user_data"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    experience: Mapped[int] = mapped_column(default=0)
    level: Mapped[int] = mapped_column(default=1)
    coins: Mapped[int] = mapped_column(default=0)
    last_daily: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<UserData(user_id={self.user_id}, level={self.level}, xp={self.experience})>"
