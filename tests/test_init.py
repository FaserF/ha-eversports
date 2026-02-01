"""Test Eversports initialization."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.eversports.const import DOMAIN
from tests.const import MOCK_CONFIG


async def test_setup_unload_entry(hass: HomeAssistant) -> None:
    """Test setup and unload of a config entry."""
    entry = hass.config_entries.async_add_entry(
        config_entries.ConfigEntry(
            version=1,
            domain=DOMAIN,
            title="Eversports Squash",
            data=MOCK_CONFIG,
            source="user",
            entry_id="test_entry",
        )
    )

    with patch(
        "custom_components.eversports.EversportsDataUpdateCoordinator._async_update_data",
        return_value={},
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]
