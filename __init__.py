"""The Strasbourg Parkings integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PARKINGS, DOMAIN
from .sensor import StrasbourgParkingCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Strasbourg Parkings from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    selected_parkings = entry.data[CONF_PARKINGS]
    coordinators: dict[str, StrasbourgParkingCoordinator] = {}

    for parking_id in selected_parkings:
        coordinator = StrasbourgParkingCoordinator(hass, parking_id, entry)
        await coordinator.async_config_entry_first_refresh()
        coordinators[parking_id] = coordinator

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
