from datetime import datetime, date
import re

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)

from homeassistant.helpers.entity import DeviceInfo

from homeassistant.const import (
    UnitOfMass,
    UnitOfPower,
    UnitOfLength,
)

from .const import DOMAIN


DROP_SEGMENTS = {
    "kjoretoydataListe",
    "godkjenning",
    "tekniskGodkjenning",
    "tekniskeData"
}


NAME_MAP = {
    "kontrollfrist": "EU Kontroll Frist",
    "sistgodkjent": "EU Kontroll Sist Godkjent"
}


def flatten(data, parent_key="", result=None):

    if result is None:
        result = {}

    if isinstance(data, dict):

        for key, value in data.items():

            new_key = f"{parent_key}_{key}" if parent_key else key

            flatten(value, new_key, result)

    elif isinstance(data, list):

        for index, value in enumerate(data):

            new_key = f"{parent_key}_{index}"

            flatten(value, new_key, result)

    else:

        result[parent_key] = data

    return result


def clean_key(key):

    parts = key.split("_")

    cleaned = []

    for p in parts:

        if p.isdigit():
            continue

        if p in DROP_SEGMENTS:
            continue

        cleaned.append(p)

    if len(cleaned) > 3:
        cleaned = cleaned[-3:]

    result = "_".join(cleaned)

    result = re.sub(r'([a-z])([A-Z])', r'\1_\2', result)

    return result.lower()


def guess_unit(key):

    key = key.lower()

    if "vekt" in key:
        return UnitOfMass.KILOGRAMS

    if "effekt" in key:
        return UnitOfPower.KILO_WATT

    if "lengde" in key or "bredde" in key or "hoyde" in key:
        return UnitOfLength.MILLIMETERS

    if "rekkevidde" in key:
        return "km"

    return None


def guess_device_class(key):

    key = key.lower()

    if "dato" in key or "frist" in key:
        return SensorDeviceClass.DATE

    if "effekt" in key:
        return SensorDeviceClass.POWER

    if "vekt" in key:
        return SensorDeviceClass.WEIGHT

    if "lengde" in key or "bredde" in key or "hoyde" in key:
        return SensorDeviceClass.DISTANCE

    return None


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    data = coordinator.data

    if not data:
        return

    plate = coordinator.plate

    flat = flatten(data)

    sensors = []

    for raw_key in flat.keys():

        parts = raw_key.split("_")

        # hopp over array-elementer >0
        if any(p.isdigit() and p != "0" for p in parts):
            continue

        clean = clean_key(raw_key)

        sensors.append(
            VegvesenSensor(
                coordinator,
                plate,
                clean,
                raw_key
            )
        )

    sensors.append(EUCountdownSensor(coordinator, plate))

    async_add_entities(sensors)


class VegvesenSensor(SensorEntity):

    def __init__(self, coordinator, plate, clean_key, raw_key):

        self.coordinator = coordinator
        self.plate = plate
        self.key = clean_key
        self.raw_key = raw_key

        self._attr_native_unit_of_measurement = guess_unit(clean_key)
        self._attr_device_class = guess_device_class(clean_key)

        if "effekt" in clean_key:
            self._attr_icon = "mdi:engine"

        elif "vekt" in clean_key:
            self._attr_icon = "mdi:weight"

        elif "drivstoff" in clean_key:
            self._attr_icon = "mdi:gas-station"

        elif "rekkevidde" in clean_key:
            self._attr_icon = "mdi:map-marker-distance"

        else:
            self._attr_icon = "mdi:car-info"

    @property
    def unique_id(self):
        return f"{self.plate}_{self.raw_key}"

    @property
    def name(self):

        if self.key in NAME_MAP:
            return NAME_MAP[self.key]

        return self.key.replace("_", " ").title()

    @property
    def native_value(self):

        flat = flatten(self.coordinator.data)

        value = flat.get(self.raw_key)

        if self._attr_device_class == SensorDeviceClass.DATE and value:

            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except Exception:
                return None

        return value

    @property
    def device_info(self):

        data = self.coordinator.data or {}

        generelt = (
            data.get("godkjenning", {})
            .get("tekniskGodkjenning", {})
            .get("tekniskeData", {})
            .get("generelt", {})
        )

        merke = None
        modell = None

        merke_list = generelt.get("merke")

        if isinstance(merke_list, list) and merke_list:
            merke = merke_list[0].get("merke")

        modell_list = generelt.get("handelsbetegnelse")

        if isinstance(modell_list, list) and modell_list:
            modell = modell_list[0]

        name = self.plate

        if merke and modell:
            name = f"{merke} {modell} ({self.plate})"

        return DeviceInfo(
            identifiers={(DOMAIN, self.plate)},
            name=name,
            manufacturer=merke,
            model=modell,
        )


class EUCountdownSensor(SensorEntity):

    def __init__(self, coordinator, plate):

        self.coordinator = coordinator
        self.plate = plate

        self._attr_icon = "mdi:calendar-alert"

    @property
    def unique_id(self):
        return f"{self.plate}_eu_kontroll_dager"

    @property
    def name(self):
        return "EU Kontroll Dager Igjen"

    @property
    def native_value(self):

        data = self.coordinator.data or {}

        vehicle = data.get("kjoretoydataListe", [{}])[0]

        frist = (
            vehicle.get("periodiskKjoretoyKontroll", {})
            .get("kontrollfrist")
        )

        if not frist:
            return None

        try:
            frist_date = datetime.strptime(frist, "%Y-%m-%d").date()
        except Exception:
            return None

        return (frist_date - date.today()).days

    @property
    def device_info(self):

        data = self.coordinator.data or {}

        generelt = (
            data.get("godkjenning", {})
            .get("tekniskGodkjenning", {})
            .get("tekniskeData", {})
            .get("generelt", {})
        )

        merke = None
        modell = None

        merke_list = generelt.get("merke")

        if isinstance(merke_list, list) and merke_list:
            merke = merke_list[0].get("merke")

        modell_list = generelt.get("handelsbetegnelse")

        if isinstance(modell_list, list) and modell_list:
            modell = modell_list[0]

        name = self.plate

        if merke and modell:
            name = f"{merke} {modell} ({self.plate})"

        return DeviceInfo(
            identifiers={(DOMAIN, self.plate)},
            name=name,
            manufacturer=merke,
            model=modell,
        )