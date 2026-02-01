"""Test Eversports binary sensors."""

from unittest.mock import patch

from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.eversports.const import DOMAIN
from tests.const import MOCK_CONFIG


async def test_binary_sensor(hass: HomeAssistant) -> None:
    """Test binary sensor state."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Eversports Squash",
        data=MOCK_CONFIG,
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    # Test with available slots
    with patch(
        "custom_components.eversports.EversportsDataUpdateCoordinator._async_update_data",
        return_value={
            "available_slots_count": 5,
        },
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get(
        "binary_sensor.eversports_facility_12345_eversports_squash_slots_available"
    )
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

    state = hass.states.get(
        "binary_sensor.eversports_facility_12345_eversports_squash_slots_available"
    )
    assert state
    assert state.state == STATE_OFF
