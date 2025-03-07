import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

SCRIPT_SCHEMA = {
    vol.Required("on_script"): str,
    vol.Required("off_script"): str,
    vol.Required("white_script"): str,
    vol.Required("red_script"): str,
    vol.Required("green_script"): str,
    vol.Required("blue_script"): str,
}

class LightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the light."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate inputs (optional, extend as needed)
            try:
                return self.async_create_entry(title="Custom Light", data=user_input)
            except Exception as e:
                errors["base"] = "general_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(SCRIPT_SCHEMA),
            errors=errors,
        )

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up the light from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data
    return True

