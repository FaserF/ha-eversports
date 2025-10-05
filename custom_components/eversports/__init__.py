# custom_components/eversports/__init__.py
"""The Eversports integration."""
from datetime import datetime
import pytz

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    LOGGER,
    PLATFORMS,
    UPDATE_INTERVAL,
    BASE_URL,
    CONF_FACILITY_ID,
    CONF_SPORT,
    CONF_COURT_IDS,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eversports from a config entry."""
    session = async_get_clientsession(hass)
    config = entry.data

    facility_id = config[CONF_FACILITY_ID]
    sport = config[CONF_SPORT]
    court_ids_str = config[CONF_COURT_IDS]
    # Split string and build the court query part of the URL
    court_params = "&".join(
        [f"courts[]={court_id.strip()}" for court_id in court_ids_str.split(",")]
    )

    async def _async_update_data():
        """Fetch data from API."""
        # Get current date in the correct format for the API
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Construct the full URL
        url = f"{BASE_URL}?facilityId={facility_id}&sport={sport}&startDate={today_str}&{court_params}"

        # These headers are crucial to get a valid response
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://www.eversports.de/widget/w/{facility_id}",
        }

        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                LOGGER.debug(f"API response received: {data}")
                return process_eversports_data(data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"Eversports {sport}",
        update_method=_async_update_data,
        update_interval=UPDATE_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


def process_eversports_data(data):
    """Process the JSON data from the Eversports API."""
    now = datetime.now(pytz.timezone("Europe/Berlin"))

    # Filter for slots that are not booked ("present": false) and are in the future
    available_slots = [
        slot
        for slot in data.get("slots", [])
        if not slot.get("present")
        and f"{slot['date']} {slot['start']}" >= now.strftime("%Y-%m-%d %H%M")
    ]

    # Sort available slots by time
    available_slots.sort(key=lambda x: x["start"])

    if not available_slots:
        return {
            "next_available_slot": None,
            "total_slots": len(data.get("slots", [])),
            "available_slots_count": 0,
            "available_slots_list": [],
        }

    next_slot = available_slots[0]

    # Format time string from "1630" to "16:30"
    start_time_str = f"{next_slot['start'][:2]}:{next_slot['start'][2:]}"

    # Create datetime object for the next slot
    next_slot_dt = datetime.strptime(
        f"{next_slot['date']} {start_time_str}", "%Y-%m-%d %H:%M"
    ).astimezone(pytz.timezone("Europe/Berlin"))

    return {
        "next_available_slot": start_time_str,
        "next_slot_datetime": next_slot_dt.isoformat(),
        "next_slot_court_id": next_slot.get("court"),
        "total_slots": len(data.get("slots", [])),
        "available_slots_count": len(available_slots),
        "available_slots_list": [
            f"{s['start'][:2]}:{s['start'][2:]}" for s in available_slots
        ],
    }


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
