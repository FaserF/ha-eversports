# custom_components/eversports/config_flow.py
"""Config flow for Eversports integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_FACILITY_ID, CONF_SPORT, CONF_COURT_IDS

class EversportsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eversports."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Create a unique ID to prevent duplicate entries
            unique_id = f"{user_input[CONF_FACILITY_ID]}_{user_input[CONF_SPORT]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Create the config entry
            title = f"Eversports {user_input[CONF_SPORT].capitalize()}"
            return self.async_create_entry(title=title, data=user_input)

        # Define the schema for the user form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_FACILITY_ID): str,
                vol.Required(CONF_SPORT): str,
                vol.Required(CONF_COURT_IDS): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )