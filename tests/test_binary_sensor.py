"""Test Eversports binary sensors."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant

from custom_components.eversports.const import DOMAIN
from .const import MOCK_CONFIG


async def test_binary_sensor(hass: HomeAssistant) -> None:
    """Test binary sensor state."""
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

    # Test with available slots
    with patch(
        "custom_components.eversports.EversportsDataUpdateCoordinator._async_update_data",
        return_value={
            "available_slots_count": 5,
        },
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.eversports_squash_slots_available")
    assert state
    assert state.state == STATE_ON
    assert state.attributes["available_slots_count"] == 5

    # Test with NO available slots
    with patch(
        "custom_components.eversports.EversportsDataUpdateCoordinator._async_update_data",
        return_value={
            "available_slots_count": 0,
        },
    ):
        # Trigger update
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_refresh()
        await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.eversports_squash_slots_available")
    assert state
    assert state.state == STATE_OFF
