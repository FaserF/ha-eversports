# custom_components/eversports/sensor.py
"""Sensor platform for Eversports."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EversportsDataUpdateCoordinator
from .const import CONF_COURT_IDS, CONF_FACILITY_ID, CONF_SPORT, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: EversportsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    description = SensorEntityDescription(
        key="next_available",
        name=f"Eversports {entry.data[CONF_SPORT].capitalize()} Next Available",
        icon="mdi:racquetball",
    )

    async_add_entities([EversportsSensor(coordinator, entry, description)])


class EversportsSensor(
    CoordinatorEntity[EversportsDataUpdateCoordinator], SensorEntity
):
    """Eversports Sensor class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EversportsDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data and (
            val := self.coordinator.data.get("next_available_slot")
        ):
            return val
        return "Keine freien Slots"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        if not data:
            return {}

        # Exclude data used in state or attribution from the attributes dict
        attributes_data = data.copy()
        attributes_data.pop("next_available_slot", None)

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
