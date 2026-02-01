"""Config flow for Strasbourg Parkings integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import API_BASE_URL, CONF_PARKINGS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _fetch_parkings_list(session: aiohttp.ClientSession) -> dict[str, str]:
    """Fetch available parkings from the API.

    Returns a dict of {idsurfs: nom_parking} sorted by name.
    """
    url = f"{API_BASE_URL}?select=idsurfs,nom_parking&limit=100"
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.json()

    parkings: dict[str, str] = {}
    for record in data.get("results", []):
        idsurfs = record.get("idsurfs")
        nom = record.get("nom_parking")
        if idsurfs and nom:
            parkings[idsurfs] = nom

    return dict(sorted(parkings.items(), key=lambda x: x[1]))


class StrasbourgParkingsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Strasbourg Parkings."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return StrasbourgParkingsOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        session = async_get_clientsession(self.hass)

        if user_input is not None:
            selected = user_input.get(CONF_PARKINGS, [])
            if not selected:
                errors["base"] = "no_parking_selected"
            else:
                return self.async_create_entry(
                    title=f"Strasbourg Parkings ({len(selected)})",
                    data={CONF_PARKINGS: selected},
                )

        try:
            parkings = await _fetch_parkings_list(session)
        except (aiohttp.ClientError, TimeoutError):
            errors["base"] = "cannot_connect"
            parkings = {}

        if not parkings and "base" not in errors:
            errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PARKINGS, default=[]): cv.multi_select(parkings),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class StrasbourgParkingsOptionsFlow(OptionsFlow):
    """Handle options flow for Strasbourg Parkings."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        session = async_get_clientsession(self.hass)

        if user_input is not None:
            selected = user_input.get(CONF_PARKINGS, [])
            if not selected:
                errors["base"] = "no_parking_selected"
            else:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={CONF_PARKINGS: selected},
                )
                return self.async_create_entry(data={})

        try:
            parkings = await _fetch_parkings_list(session)
        except (aiohttp.ClientError, TimeoutError):
            errors["base"] = "cannot_connect"
            parkings = {}

        current = self.config_entry.data.get(CONF_PARKINGS, [])

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PARKINGS, default=current): cv.multi_select(
                    parkings
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
