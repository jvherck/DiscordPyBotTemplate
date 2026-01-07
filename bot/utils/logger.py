"""
Custom logging configuration with color support and rotation.

Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

import colorlog

if TYPE_CHECKING:
    from bot.core.config import BotConfig


class BotLogger:
    """Custom logger for the Discord bot."""

    def __init__(self, name: str, config: BotConfig):
        """
        Initialize the bot logger.

        Args:
            name: Logger name
            config: Bot configuration
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level.value))
        self.logger.handlers.clear()
        self.logger.propagate = False

        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.log_level.value))

        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s%(reset)s | "
            "%(log_color)s%(levelname)-8s%(reset)s | "
            "%(cyan)s%(name)s%(reset)s | "
            "%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation
        if config.log_to_file:
            log_path = Path(config.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=config.log_file_path,
                maxBytes=config.log_max_bytes,
                backupCount=config.log_backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(getattr(logging, config.log_level.value))

            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


def setup_logger(name: str, config: BotConfig) -> BotLogger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name
        config: Bot configuration

    Returns:
        Configured BotLogger instance
    """
    return BotLogger(name, config)


def setup_discord_logging(config: BotConfig) -> None:
    """
    Configure Discord.py library logging.

    Args:
        config: Bot configuration
    """
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.INFO if config.debug_mode else logging.WARNING)

    # Only add handlers if none exist
    if not discord_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | discord | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        discord_logger.addHandler(handler)
