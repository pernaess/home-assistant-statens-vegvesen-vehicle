import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class StatensVegvesenVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            plate = user_input["license_plate"].upper()

            await self.async_set_unique_id(plate)

            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Vehicle {plate}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("license_plate"): str,
                vol.Required("api_key"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )