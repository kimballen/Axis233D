from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
import voluptuous as vol
from .const import DOMAIN, CONF_HTTP_PORT, DEFAULT_HTTP_PORT, DEFAULT_USERNAME
from .axis_io import Axis233DIO

class Axis233DConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Test connection
            camera = Axis233DIO(
                user_input[CONF_HOST],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                http_port=user_input[CONF_HTTP_PORT],
            )

            success = await self.hass.async_add_executor_job(camera.test_connection)
            
            if success:
                return self.async_create_entry(
                    title=f"Axis Camera {user_input[CONF_HOST]}", 
                    data=user_input
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_HTTP_PORT, default=DEFAULT_HTTP_PORT): int,
            }),
            errors=errors,
        )
