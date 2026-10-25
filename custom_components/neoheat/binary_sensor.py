"""Empirically mapped read-only binary sensors."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


# Runtime fields confirmed against the cloud application's P0/P1/P2 values.
PUMPS = (
    (151, "Pump P0"),
    (155, "Pump P1"),
    (159, "Pump P2"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(NeoheatPumpBinarySensor(entry, offset, name) for offset, name in PUMPS)


class NeoheatPumpBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Expose a pump output as an on/off state without writing to the device."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, entry, offset, name):
        super().__init__(entry.runtime_data)
        self.offset = offset
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_pump_{offset}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Neoheat",
            manufacturer="Neoheat",
            model="EKO II (experimental local protocol)",
        )

    @property
    def available(self):
        return super().available and self.offset in (self.coordinator.data or {}).get(1, {})

    @property
    def is_on(self):
        value = (self.coordinator.data or {}).get(1, {}).get(self.offset)
        return value >= 0.5 if value is not None else None
