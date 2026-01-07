"""
Discord Bot Template
Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

__version__ = "0.1.0"
__author__ = "Jan Van Herck"

from bot.core.bot import DiscordBot
from bot.core.config import BotConfig

__all__ = ["DiscordBot", "BotConfig", "__version__", "__author__"]
