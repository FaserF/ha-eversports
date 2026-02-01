"""Test Eversports sensors."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.eversports.const import DOMAIN
from .const import MOCK_CONFIG


async def test_sensor(hass: HomeAssistant) -> None:
    """Test sensor state and attributes."""
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
        return_value={
            "next_available_slot": "18:00",
            "next_slot_datetime": "2026-02-01T18:00:00",
            "next_slot_court_id": "52463",
            "total_slots": 10,
            "available_slots_count": 5,
            "available_slots_list": ["18:00", "19:00"],
            "last_update": "2026-02-01T14:00:00",
            "api_url": "http://api.test",
        },
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.eversports_squash_next_available")
    assert state
    assert state.state == "18:00"
    assert state.attributes["next_slot_court_id"] == "52463"
    assert state.attributes["available_slots_count"] == 5
    assert state.attributes["facility_id"] == MOCK_CONFIG["facility_id"]
