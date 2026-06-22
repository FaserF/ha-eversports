# custom_components/eversports/__init__.py
"""The Eversports integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from aiohttp import ClientTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import (
    BASE_URL,
    CONF_COURT_IDS,
    CONF_FACILITY_ID,
    CONF_SPORT,
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL,
)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CALENDAR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eversports from a config entry."""
    coordinator = EversportsDataUpdateCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class EversportsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Eversports data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.facility_id = entry.data[CONF_FACILITY_ID]
        self.sport = entry.data[CONF_SPORT]
        court_ids_str = entry.data[CONF_COURT_IDS]
        self.court_params = "&".join(
            [f"courts[]={court_id.strip()}" for court_id in court_ids_str.split(",")]
        )
        self.last_success = dt_util.utcnow()

        super().__init__(
            hass,
            LOGGER,
            name=f"Eversports {self.sport}",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        session = async_get_clientsession(self.hass)
        now = dt_util.now()
        today_str = now.strftime("%Y-%m-%d")

        url = f"{BASE_URL}?facilityId={self.facility_id}&sport={self.sport}&startDate={today_str}&{self.court_params}"
        LOGGER.debug("Requesting URL: %s", url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://www.eversports.de/widget/w/{self.facility_id}",
        }

        try:
            async with session.get(url, headers=headers, timeout=ClientTimeout(total=10)) as response:
                response.raise_for_status()
                data = await response.json()
                LOGGER.debug("Full API response received: %s", data)
                processed_data = self.process_eversports_data(data, url, now)
                LOGGER.debug("Processed data: %s", processed_data)

                # Reset repair if it was active
                ir.async_delete_issue(
                    self.hass, DOMAIN, f"data_fetch_failed_{self.entry.entry_id}"
                )
                self.last_success = dt_util.utcnow()

                return processed_data
        except Exception as err:
            # Check if last success was more than 24 hours ago
            if dt_util.utcnow() - self.last_success > timedelta(hours=24):
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    f"data_fetch_failed_{self.entry.entry_id}",
                    is_fixable=False,
                    severity=ir.IssueSeverity.ERROR,
                    translation_key="data_fetch_failed",
                    translation_placeholders={
                        "facility_id": self.facility_id,
                        "sport": self.sport,
                    },
                    learn_more_url="https://github.com/FaserF/ha-eversports/issues",
                )
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def process_eversports_data(self, data: dict, api_url: str, now: datetime) -> dict:
        """Process the JSON data from the Eversports API."""
        today_str = now.strftime("%Y-%m-%d")
        LOGGER.debug("Processing data at current time: %s", now.isoformat())

        raw_slots = data.get("slots", [])
        LOGGER.debug("Found %s total slots in response", len(raw_slots))

        # 1. Find all available slots in the future
        future_available_slots = [
            slot
            for slot in raw_slots
            if not slot.get("present")
            and f"{slot['date']} {slot['start']}" >= now.strftime("%Y-%m-%d %H%M")
        ]
        LOGGER.debug(
            "Found %s available slots in the future", len(future_available_slots)
        )

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

        # Combine date and time to create a datetime object
        next_slot_dt = dt_util.parse_datetime(f"{next_slot['date']} {start_time_str}")
        if next_slot_dt:
            next_slot_dt = dt_util.as_local(next_slot_dt)

        return {
            "next_available_slot": display_state,
            "next_slot_datetime": next_slot_dt.isoformat() if next_slot_dt else None,
            "next_slot_court_id": next_slot.get("court"),
            "total_slots": len(raw_slots),
            "available_slots_count": len(future_available_slots),
            "available_slots_list": todays_available_times,
            "last_update": now.isoformat(),
            "api_url": api_url,
            "all_slots": self._process_all_slots(future_available_slots, now),
        }

    def _process_all_slots(self, slots: list[dict], now: datetime) -> list[dict]:
        """Process all slots into a format suitable for the calendar."""
        processed_slots = []
        for slot in slots:
            start_raw = slot.get("start")
            end_raw = slot.get("end")

            # Validate that we have valid 4-digit strings for slicing
            if (
                not isinstance(start_raw, str)
                or len(start_raw) < 4
                or not isinstance(end_raw, str)
                or len(end_raw) < 4
            ):
                continue

            start_str = f"{start_raw[:2]}:{start_raw[2:]}"
            end_str = f"{end_raw[:2]}:{end_raw[2:]}"

            start_dt = dt_util.parse_datetime(f"{slot['date']} {start_str}")
            end_dt = dt_util.parse_datetime(f"{slot['date']} {end_str}")

            if start_dt and end_dt:
                processed_slots.append(
                    {
                        "start": dt_util.as_local(start_dt),
                        "end": dt_util.as_local(end_dt),
                    }
                )
        return processed_slots
