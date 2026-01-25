"""Config flow for Strasbourg Parkings integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_PARKINGS, PARKINGS_LIST

_LOGGER = logging.getLogger(__name__)


class StrasbourgParkingsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Strasbourg Parkings."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Vérifier qu'au moins un parking est sélectionné
            selected_parkings = user_input.get(CONF_PARKINGS, [])
            
            if not selected_parkings:
                errors["base"] = "no_parking_selected"
            else:
                # Créer un titre basé sur le nombre de parkings sélectionnés
                title = f"Strasbourg Parkings ({len(selected_parkings)})"
                
                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )

        # Créer le formulaire avec des checkboxes pour chaque parking
        data_schema = vol.Schema(
            {
                vol.Required(CONF_PARKINGS, default=[]): cv.multi_select(PARKINGS_LIST),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "parkings_count": str(len(PARKINGS_LIST))
            },
        )
