# custom_components/eversports/__init__.py
"""The Eversports integration."""
from datetime import datetime, timedelta
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
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        today_str = now.strftime("%Y-%m-%d")

        # Construct the full URL
        url = f"{BASE_URL}?facilityId={facility_id}&sport={sport}&startDate={today_str}&{court_params}"
        LOGGER.debug(f"Requesting URL: {url}")

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
                LOGGER.debug(f"Full API response received: {data}")
                processed_data = process_eversports_data(data, url, now)
                LOGGER.debug(f"Processed data: {processed_data}")
                return processed_data
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


def process_eversports_data(data, api_url: str, now: datetime):
    """Process the JSON data from the Eversports API."""
    today_str = now.strftime("%Y-%m-%d")
    LOGGER.debug(f"Processing data at current time: {now.isoformat()}")

    raw_slots = data.get("slots", [])
    LOGGER.debug(f"Found {len(raw_slots)} total slots in response.")

    # 1. Find all available slots in the future
    future_available_slots = [
        slot
        for slot in raw_slots
        if not slot.get("present")
        and f"{slot['date']} {slot['start']}" >= now.strftime("%Y-%m-%d %H%M")
    ]
    LOGGER.debug(f"Found {len(future_available_slots)} available slots in the future.")

    # Sort them chronologically
    future_available_slots.sort(key=lambda x: (x["date"], x["start"]))

    # 2. Find all available slots for TODAY for the attribute list
    todays_available_slots = [
        slot for slot in future_available_slots if slot["date"] == today_str
    ]
    todays_available_times = sorted(
        [f"{s['start'][:2]}:{s['start'][2:]}" for s in todays_available_slots]
    )

    # 3. Determine state and attributes
    if not future_available_slots:
        return {
            "next_available_slot": None,
            "next_slot_datetime": None,
            "next_slot_court_id": None,
            "total_slots": len(raw_slots),
            "available_slots_count": 0,
            "available_slots_list": [],
            "last_update": now.isoformat(),
            "api_url": api_url,
        }

    next_slot = future_available_slots[0]
    start_time_str = f"{next_slot['start'][:2]}:{next_slot['start'][2:]}"

    # Format display state
    display_state = start_time_str
    next_date_obj = datetime.strptime(next_slot["date"], "%Y-%m-%d").date()
    today_date_obj = now.date()
    if next_slot["date"] != today_str:
        if (next_date_obj - today_date_obj).days == 1:
            display_state = f"Morgen, {start_time_str}"
        else:
            display_state = f"{next_date_obj.strftime('%d.%m')}, {start_time_str}"

    next_slot_dt = now.tzinfo.localize(
        datetime.strptime(f"{next_slot['date']} {start_time_str}", "%Y-%m-%d %H:%M")
    )

    return {
        "next_available_slot": display_state,
        "next_slot_datetime": next_slot_dt.isoformat(),
        "next_slot_court_id": next_slot.get("court"),
        "total_slots": len(raw_slots),
        "available_slots_count": len(future_available_slots),
        "available_slots_list": todays_available_times,
        "last_update": now.isoformat(),
        "api_url": api_url,
    }


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
