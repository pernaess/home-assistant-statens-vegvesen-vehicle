import logging

from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VegvesenAPI
from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class VegvesenCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, config):

        self.hass = hass

        self.plate = config["license_plate"]
        self.api_key = config["api_key"]

        session = async_get_clientsession(hass)

        self.api = VegvesenAPI(session, self.plate, self.api_key)

        super().__init__(
            hass,
            _LOGGER,
            name="vegvesen_vehicle",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):

        return await self.api.get_vehicle()