"""Binary sensor platform for Eversports."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EversportsDataUpdateCoordinator
from .const import CONF_FACILITY_ID, CONF_SPORT, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: EversportsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    description = BinarySensorEntityDescription(
        key="slots_available",
        name=f"Eversports {entry.data[CONF_SPORT].capitalize()} Slots Available",
        icon="mdi:calendar-check",
    )

    async_add_entities([EversportsBinarySensor(coordinator, entry, description)])


class EversportsBinarySensor(
    CoordinatorEntity[EversportsDataUpdateCoordinator], BinarySensorEntity
):
    """Eversports Binary Sensor class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EversportsDataUpdateCoordinator,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_binary_sensor"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("available_slots_count", 0) > 0

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        return {
            "available_slots_count": self.coordinator.data.get(
                "available_slots_count", 0
            ),
            "facility_id": self.entry.data[CONF_FACILITY_ID],
        }

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.entry.data[CONF_FACILITY_ID])},
            "name": f"Eversports Facility {self.entry.data[CONF_FACILITY_ID]}",
            "manufacturer": "Eversports",
            "configuration_url": f"https://www.eversports.de/s/{self.entry.data[CONF_FACILITY_ID]}",
        }
