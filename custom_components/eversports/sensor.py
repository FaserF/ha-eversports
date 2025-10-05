# custom_components/eversports/sensor.py
"""Sensor platform for Eversports."""
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_FACILITY_ID, CONF_SPORT, CONF_COURT_IDS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EversportsSensor(coordinator, entry)])


class EversportsSensor(CoordinatorEntity, SensorEntity):
    """Eversports Sensor class."""

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._sport = entry.data[CONF_SPORT].capitalize()
        self._attr_name = f"Eversports {self._sport} Next Available"
        self._attr_icon = "mdi:racquetball"  # Generic icon, can be changed

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return self.entry.entry_id

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data and data.get("next_available_slot"):
            return data["next_available_slot"]
        return "Keine freien Slots"

    @property
    def attribution(self) -> str | None:
        """Return the attribution."""
        if not self.coordinator.data:
            return None

        last_update_iso = self.coordinator.data.get("last_update")
        api_url = self.coordinator.data.get("api_url")

        if not last_update_iso or not api_url:
            return None

        last_update_dt = datetime.fromisoformat(last_update_iso)
        last_update_str = last_update_dt.strftime("%Y-%m-%d %H:%M:%S")

        return f"Last update: {last_update_str} from {api_url}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        if not data:
            return {}

        # Exclude data used in state or attribution from the attributes dict
        attributes_data = data.copy()
        attributes_data.pop("next_available_slot", None)
        attributes_data.pop("last_update", None)
        attributes_data.pop("api_url", None)

        # Add config data for reference
        attributes_data["facility_id"] = self.entry.data[CONF_FACILITY_ID]
        attributes_data["sport"] = self.entry.data[CONF_SPORT]
        attributes_data["monitored_courts"] = self.entry.data[CONF_COURT_IDS]

        return attributes_data

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.entry.data[CONF_FACILITY_ID])},
            "name": f"Eversports Facility {self.entry.data[CONF_FACILITY_ID]}",
            "manufacturer": "Eversports",
            "configuration_url": f"https://www.eversports.de/s/{self.entry.data[CONF_FACILITY_ID]}",
        }
