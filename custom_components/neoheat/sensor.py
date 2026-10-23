"""Empirically mapped read-only sensors."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

# (frame type, byte offset, name, unit, device class, default enabled)
FIELDS = [
    (1, 35, "Outlet temperature Tuo", "°C", "temperature", True),
    (1, 39, "Inlet temperature Tui", "°C", "temperature", True),
    (1, 43, "Temperature Tup", "°C", "temperature", False),
    (1, 47, "DHW temperature TW", "°C", "temperature", True),
    (1, 51, "Heating cooling temperature TC", "°C", "temperature", True),
    (1, 55, "Circuit 1 temperature TV1", "°C", "temperature", True),
    (1, 59, "Circuit 2 temperature TV2", "°C", "temperature", True),
    (1, 63, "Room temperature TR", "°C", "temperature", True),
    (1, 99, "Compressor frequency", "Hz", "frequency", True),
    (1, 103, "Valve opening raw", None, None, False),
    (1, 107, "Pressure Pd raw", None, None, False),
    (1, 111, "Pressure Ps raw", None, None, False),
    (1, 115, "Outdoor temperature Ta", "°C", "temperature", True),
    (1, 119, "Temperature Td", "°C", "temperature", True),
    (1, 123, "Temperature Ts", "°C", "temperature", True),
    (1, 127, "Temperature Tp", "°C", "temperature", True),
    (1, 131, "Fan 1 speed", "rpm", None, True),
    (1, 135, "Fan 2 speed", "rpm", None, True),
    (1, 139, "Current", "A", "current", True),
    (1, 143, "Voltage", "V", "voltage", True),
    (1, 151, "Pump P0 raw", None, None, False),
    (1, 155, "Pump P1 raw", None, None, False),
    (1, 159, "Pump P2 raw", None, None, False),
    (1, 163, "Active target temperature", "°C", "temperature", True),
    (1, 167, "Software version", None, None, True),
    (1, 183, "Auxiliary heater runtime", "min", "duration", False),
    (2, 163, "Circuit 1 heating setpoint", "°C", "temperature", False),
    (2, 231, "DHW setpoint", "°C", "temperature", False),
    (2, 271, "DHW reheat setpoint", "°C", "temperature", False),
    (2, 311, "Circuit 2 heating setpoint", "°C", "temperature", False),
    (2, 23, "Database version", None, None, False),
    (2, 559, "Heat pump PCB version", None, None, False),
    (2, 563, "Outdoor EEPROM version", None, None, False),
]


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(NeoheatSensor(entry, field) for field in FIELDS)


class NeoheatSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry, field):
        super().__init__(entry.runtime_data)
        self.kind, self.offset, name, unit, device_class, enabled = field
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{self.kind}_{self.offset}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = SensorDeviceClass(device_class) if device_class else None
        self._attr_entity_registry_enabled_default = enabled
        if unit and self.kind == 1 and self.offset not in (163, 183):
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if not enabled or self.offset == 167:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name="Neoheat",
            manufacturer="Neoheat", model="EKO II (experimental local protocol)",
        )

    @property
    def available(self):
        return super().available and self.offset in (self.coordinator.data or {}).get(self.kind, {})

    @property
    def native_value(self):
        value = (self.coordinator.data or {}).get(self.kind, {}).get(self.offset)
        return round(value, 2) if value is not None else None
