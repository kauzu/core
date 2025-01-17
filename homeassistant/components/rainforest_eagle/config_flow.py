"""Config flow for Rainforest Eagle integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_TYPE
from homeassistant.data_entry_flow import FlowResult

from . import data
from .const import CONF_CLOUD_ID, CONF_HARDWARE_ADDRESS, CONF_INSTALL_CODE, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLOUD_ID): str,
        vol.Required(CONF_INSTALL_CODE): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rainforest Eagle."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        await self.async_set_unique_id(user_input[CONF_CLOUD_ID])
        errors = {}

        try:
            eagle_type, hardware_address = await data.async_get_type(
                self.hass, user_input[CONF_CLOUD_ID], user_input[CONF_INSTALL_CODE]
            )
        except data.CannotConnect:
            errors["base"] = "cannot_connect"
        except data.InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            user_input[CONF_TYPE] = eagle_type
            user_input[CONF_HARDWARE_ADDRESS] = hardware_address
            return self.async_create_entry(
                title=user_input[CONF_CLOUD_ID], data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        """Handle the import step."""
        await self.async_set_unique_id(user_input[CONF_CLOUD_ID])
        self._abort_if_unique_id_configured()
        return await self.async_step_user(user_input)
