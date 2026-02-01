"""Calendar platform for Eversports."""

from __future__ import annotations
from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EversportsDataUpdateCoordinator
from .const import CONF_SPORT, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    coordinator: EversportsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([EversportsCalendar(coordinator, entry)])


class EversportsCalendar(
    CoordinatorEntity[EversportsDataUpdateCoordinator], CalendarEntity
):
    """Eversports Calendar class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EversportsDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the calendar."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"Eversports {entry.data[CONF_SPORT].capitalize()}"
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self._get_events()
        if events:
            return events[0]
        return None

    def _get_events(self) -> list[CalendarEvent]:
        """Get all available slots as events."""
        if not self.coordinator.data or "all_slots" not in self.coordinator.data:
            return []

        return [
            CalendarEvent(
                summary=f"Free {self.entry.data[CONF_SPORT].capitalize()} Slot",
                start=slot["start"],
                end=slot["end"],
                location=f"Facility {self.entry.data.get('facility_id')}",
            )
            for slot in self.coordinator.data["all_slots"]
        ]

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self._get_events()
        return [
            event
            for event in events
            if event.start >= start_date and event.end <= end_date
        ]
