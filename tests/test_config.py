"""Tests for configuration management."""

import pytest

from bot.core.config import BotConfig, Environment, LogLevel


def test_config_defaults():
    """Test default configuration values."""
    config = BotConfig(discord_token="test_token")

    assert config.discord_token == "test_token"
    assert config.discord_prefix == "!"
    assert config.bot_name == "MyDiscordBot"
    assert config.environment == Environment.DEVELOPMENT
    assert config.log_level == LogLevel.INFO


def test_config_is_production():
    """Test production environment check."""
    config = BotConfig(discord_token="test", environment=Environment.PRODUCTION)
    assert config.is_production is True
    assert config.is_development is False


def test_config_is_development():
    """Test development environment check."""
    config = BotConfig(discord_token="test", environment=Environment.DEVELOPMENT)
    assert config.is_development is True
    assert config.is_production is False


def test_config_intents():
    """Test Discord intents configuration."""
    config = BotConfig(discord_token="test")
    intents = config.get_intents()

    assert isinstance(intents, dict)
    assert intents["guilds"] is True
    assert intents["messages"] is True
    assert intents["message_content"] is True
