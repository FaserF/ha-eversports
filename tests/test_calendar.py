"""Test Eversports calendar."""

from datetime import datetime
from unittest.mock import patch
import pytz

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.eversports.const import DOMAIN
from .const import MOCK_CONFIG


async def test_calendar(hass: HomeAssistant) -> None:
    """Test calendar events."""
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

    tz = pytz.timezone("Europe/Berlin")
    start_time = tz.localize(datetime(2026, 2, 1, 10, 0, 0))
    end_time = tz.localize(datetime(2026, 2, 1, 11, 0, 0))

    with patch(
        "custom_components.eversports.EversportsDataUpdateCoordinator._async_update_data",
        return_value={
            "all_slots": [
                {
                    "start": start_time,
                    "end": end_time,
                }
            ],
        },
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("calendar.eversports_squash")
    assert state
    assert state.state == "on"
