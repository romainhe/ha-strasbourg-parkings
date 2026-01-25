"""Sensor platform for Strasbourg Parkings."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

# from homeassistant.components.sensor import SensorEntity, SensorStateClass
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

from .const import API_BASE_URL, DOMAIN, PARKINGS_API_IDS, PARKINGS_LIST, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Strasbourg Parkings sensors from a config entry."""
    # Get pre-initialized coordinators from hass.data
    coordinators = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    entities = [
        StrasbourgParkingSensor(coordinator, parking_id, entry.entry_id)
        for parking_id, coordinator in coordinators.items()
    ]

    async_add_entities(entities)


class StrasbourgParkingCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Strasbourg Parking data."""

    def __init__(self, hass: HomeAssistant, parking_id: str) -> None:
        """Initialize."""
        self.parking_id = parking_id
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{parking_id}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        # Get the API idsurfs value for this parking
        api_id = PARKINGS_API_IDS.get(self.parking_id)
        if not api_id:
            raise UpdateFailed(f"Unknown parking ID: {self.parking_id}")

        url = f"{API_BASE_URL}?where=idsurfs%3D%27{api_id}%27&limit=1"

        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(url)
                response.raise_for_status()
                data = await response.json()

                if not data.get("results"):
                    raise UpdateFailed(f"No data for parking {self.parking_id}")

                parking_data = data["results"][0]

                # Extract data from API response
                # API fields: libre (available), total, etat (1=open), taux_occup, nom_parking, position
                libre = parking_data.get("libre", 0)
                total = parking_data.get("total", 0)
                occupation = total - libre
                taux_occup = parking_data.get("taux_occup", 0)
                position = parking_data.get("position", {})

                return {
                    "disponible": libre,
                    "occupation": occupation,
                    "total": total,
                    "taux_occupation": round(taux_occup * 100, 1),
                    "etat": parking_data.get("etat", 0),
                    "nom": parking_data.get(
                        "nom_parking", PARKINGS_LIST[self.parking_id]
                    ),
                    "latitude": position.get("lat"),
                    "longitude": position.get("lon"),
                }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err


class StrasbourgParkingSensor(CoordinatorEntity, SensorEntity):
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
        self._attr_name = PARKINGS_LIST[parking_id]
        self._attr_unique_id = f"{entry_id}_{parking_id}"

        # Device info pour grouper les parkings
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Parkings Strasbourg",
            "manufacturer": "Eurométropole de Strasbourg",
            "model": "Open Data API",
            "entry_type": "service",
        }

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
        statut = "Ouvert" if data.get("etat") == 1 else "Fermé"

        return {
            "occupation": data.get("occupation"),
            "capacite_totale": data.get("total"),
            "taux_occupation": data.get("taux_occupation"),
            "statut": statut,
            "nom_complet": data.get("nom"),
            "parking_id": self.parking_id,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def icon(self) -> str:
        """Return icon based on parking status."""
        if not self.coordinator.data:
            return "mdi:parking"

        data = self.coordinator.data
        etat = data.get("etat", 0)
        disponible = data.get("disponible", 0)

        # Parking fermé ou plein
        if etat != 1 or disponible == 0:
            return "mdi:close-circle-outline"

        # Parking ouvert avec places disponibles
        return "mdi:parking"

    @property
    def latitude(self) -> float | None:
        """Return latitude of parking location."""
        if self.coordinator.data:
            return self.coordinator.data.get("latitude")
        return None

    @property
    def longitude(self) -> float | None:
        """Return longitude of parking location."""
        if self.coordinator.data:
            return self.coordinator.data.get("longitude")
        return None
