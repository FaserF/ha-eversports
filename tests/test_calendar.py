"""Test Eversports calendar."""

from datetime import datetime
from unittest.mock import patch
import pytz

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.eversports.const import DOMAIN
from tests.const import MOCK_CONFIG


async def test_calendar(hass: HomeAssistant, freezer) -> None:
    """Test calendar events."""
    freezer.move_to("2026-02-01T10:30:00Z")
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Eversports Squash",
        data=MOCK_CONFIG,
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

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

    state = hass.states.get("calendar.eversports_facility_12345_eversports_squash")
    assert state
    assert state.state == "on"
