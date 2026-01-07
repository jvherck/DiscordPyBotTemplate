"""Pytest configuration and fixtures."""

import asyncio

import pytest

from bot.core.config import BotConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Provide a test configuration."""
    return BotConfig(
        discord_token="test_token_123",
        discord_prefix="!test",
        bot_name="TestBot",
        database_url="sqlite:///:memory:",
        log_to_file=False,
    )
