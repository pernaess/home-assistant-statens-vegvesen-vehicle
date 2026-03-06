from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfMass, UnitOfPower


def guess_device_class(key):

    k = key.lower()

    if "vekt" in k:
        return SensorDeviceClass.WEIGHT, UnitOfMass.KILOGRAM

    if "effekt" in k:
        return SensorDeviceClass.POWER, UnitOfPower.KILO_WATT

    if "dato" in k or "frist" in k:
        return SensorDeviceClass.DATE, None

    return None, None


def guess_icon(key):

    k = key.lower()

    if "vekt" in k:
        return "mdi:weight"

    if "motor" in k:
        return "mdi:engine"

    if "drivstoff" in k:
        return "mdi:gas-station"

    if "eu" in k:
        return "mdi:calendar-alert"

    return "mdi:car-info"