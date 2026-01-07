"""
Discord Bot Template
Copyright (c) 2026 Jan Van Herck
GitHub: https://github.com/jvherck
"""

import tomllib
from pathlib import Path

# Read version from pyproject.toml
_pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
with open(_pyproject_path, "rb") as f:
    _pyproject = tomllib.load(f)
    __version__ = _pyproject["project"]["version"]

__author__ = "Jan Van Herck"

from bot.core.bot import DiscordBot
from bot.core.config import BotConfig

__all__ = ["DiscordBot", "BotConfig", "__version__", "__author__"]
