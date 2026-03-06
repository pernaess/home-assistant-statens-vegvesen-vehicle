from datetime import datetime

from homeassistant.components.binary_sensor import BinarySensorEntity

from .utils import flatten
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    plate = coordinator.plate

    async_add_entities([EUExpired(coordinator, plate)])


class EUExpired(BinarySensorEntity):

    def __init__(self, coordinator, plate):

        self.coordinator = coordinator
        self.plate = plate

    @property
    def unique_id(self):

        return f"vegvesen_{self.plate}_eu_expired"

    @property
    def name(self):

        return "EU kontroll utløpt"

    @property
    def is_on(self):

        flat = flatten(self.coordinator.data)

        date = flat.get("periodiskKjoretoyKontroll_kontrollfrist")

        if not date:
            return False

        return datetime.now() > datetime.fromisoformat(date)