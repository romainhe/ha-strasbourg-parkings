"""Sensor platform for Strasbourg Parkings."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_BASE_URL, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Strasbourg Parkings sensors from a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]

    entities = [
        StrasbourgParkingSensor(coordinator, parking_id, entry.entry_id)
        for parking_id, coordinator in coordinators.items()
    ]

    async_add_entities(entities)


class StrasbourgParkingCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Strasbourg Parking data."""

    def __init__(
        self, hass: HomeAssistant, parking_id: str, config_entry: ConfigEntry
    ) -> None:
        """Initialize."""
        self.parking_id = parking_id
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{parking_id}",
            update_interval=SCAN_INTERVAL,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        url = f"{API_BASE_URL}?where=idsurfs%3D%27{self.parking_id}%27&limit=1"

        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(url)
                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with API: {err}") from err

        if not data.get("results"):
            raise UpdateFailed(f"No data for parking {self.parking_id}")

        parking_data = data["results"][0]

        libre = parking_data.get("libre", 0)
        total = parking_data.get("total", 0)
        occupation = total - libre
        taux_occup = parking_data.get("taux_occup", 0)
        position = parking_data.get("position") or {}

        return {
            "disponible": libre,
            "occupation": occupation,
            "total": total,
            "taux_occupation": round(taux_occup * 100, 1),
            "etat": parking_data.get("etat", 0),
            "etat_descriptif": parking_data.get("etat_descriptif", "Inconnu"),
            "realtimestatus": parking_data.get("realtimestatus", ""),
            "couleur_occup": parking_data.get("couleur_occup", ""),
            "nom": parking_data.get("nom_parking", self.parking_id),
            "latitude": position.get("lat"),
            "longitude": position.get("lon"),
        }


class StrasbourgParkingSensor(CoordinatorEntity[StrasbourgParkingCoordinator], SensorEntity):
    """Representation of a Strasbourg Parking Sensor."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "places"

    def __init__(
        self,
        coordinator: StrasbourgParkingCoordinator,
        parking_id: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.parking_id = parking_id
        self._attr_unique_id = f"{entry_id}_{parking_id}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Parkings Strasbourg",
            "manufacturer": "Eurométropole de Strasbourg",
            "model": "Open Data API",
            "entry_type": "service",
        }

    @property
    def name(self) -> str | None:
        """Return the name from API data."""
        if self.coordinator.data:
            return self.coordinator.data.get("nom")
        return self.parking_id

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("disponible")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        data = self.coordinator.data

        return {
            "occupation": data.get("occupation"),
            "capacite_totale": data.get("total"),
            "taux_occupation": data.get("taux_occupation"),
            "etat": data.get("etat"),
            "etat_descriptif": data.get("etat_descriptif"),
            "realtimestatus": data.get("realtimestatus"),
            "couleur_occup": data.get("couleur_occup"),
            "nom_complet": data.get("nom"),
            "parking_id": self.parking_id,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    @property
    def icon(self) -> str:
        """Return icon based on parking real-time status."""
        if not self.coordinator.data:
            return "mdi:parking"

        data = self.coordinator.data
        status = data.get("realtimestatus", "")
        etat = data.get("etat", 0)

        # Parking closed
        if etat != 1 or status == "BLACK":
            return "mdi:close-circle-outline"

        # Full
        if status == "RED":
            return "mdi:car-off"

        # Almost full
        if status == "ORANGE":
            return "mdi:alert-circle-outline"

        # Available (GREEN, BLUE, or other)
        return "mdi:parking"
