"""The Strasbourg Parkings integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_PARKINGS, DOMAIN
from .sensor import StrasbourgParkingCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Strasbourg Parkings from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    selected_parkings = entry.data[CONF_PARKINGS]
    coordinators = {}

    # Initialize coordinators and perform first refresh
    # This can raise ConfigEntryNotReady if API is unavailable
    for parking_id in selected_parkings:
        coordinator = StrasbourgParkingCoordinator(hass, parking_id)
        await coordinator.async_config_entry_first_refresh()
        coordinators[parking_id] = coordinator

    # Store coordinators in hass.data
    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
