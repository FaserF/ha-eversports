"""Fixtures for Eversports tests."""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(hass):
    """Enable custom integrations in Home Assistant."""
    hass.data.pop("custom_components", None)
    yield


@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.eversports.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
