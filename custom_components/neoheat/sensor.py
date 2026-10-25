"""Empirically mapped read-only sensors."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, OPERATING_MODES, decode_operating_mode

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
    (1, 171, "Operating mode", None, "enum", True),
    (1, 183, "Auxiliary heater runtime", "min", "duration", False),
    (1, 187, "DHW backup heater runtime", "min", "duration", False),
    (1, 191, "Heating backup heater runtime", "min", "duration", False),
    (2, 19, "HMI software version", None, None, False),
    (2, 55, "Heating start outdoor temperature", "°C", "temperature", False),
    (2, 59, "Cooling start outdoor temperature", "°C", "temperature", False),
    (2, 91, "Circuit 1 stop delta", "°C", "temperature", False),
    (2, 95, "Circuit 1 restart delta", "°C", "temperature", False),
    (2, 99, "Compressor speed reduction delta", "°C", "temperature", False),
    (2, 103, "Circuit 1 cooling setpoint", "°C", "temperature", False),
    (2, 107, "Circuit 1 heating curve raw", None, None, False),
    (2, 111, "Heating curve outdoor point 1", "°C", "temperature", False),
    (2, 115, "Heating curve outdoor point 2", "°C", "temperature", False),
    (2, 119, "Heating curve outdoor point 3", "°C", "temperature", False),
    (2, 123, "Heating curve outdoor point 4", "°C", "temperature", False),
    (2, 127, "Heating curve outdoor point 5", "°C", "temperature", False),
    (2, 131, "Circuit 1 water curve point 1", "°C", "temperature", False),
    (2, 135, "Circuit 1 water curve point 2", "°C", "temperature", False),
    (2, 139, "Circuit 1 water curve point 3", "°C", "temperature", False),
    (2, 143, "Circuit 1 water curve point 4", "°C", "temperature", False),
    (2, 147, "Circuit 1 water curve point 5", "°C", "temperature", False),
    (2, 155, "Room heating setpoint", "°C", "temperature", False),
    (2, 159, "Room cooling setpoint", "°C", "temperature", False),
    (2, 163, "Circuit 1 heating setpoint", "°C", "temperature", False),
    (2, 175, "Anti-legionella enabled raw", None, None, False),
    (2, 179, "Anti-legionella setpoint", "°C", "temperature", False),
    (2, 183, "Anti-legionella duration", "min", "duration", False),
    (2, 187, "Anti-legionella finish time raw", None, None, False),
    (2, 191, "Vacation mode raw", None, None, False),
    (2, 195, "Vacation DHW temperature drop", "°C", "temperature", False),
    (2, 199, "Vacation heating temperature drop", "°C", "temperature", False),
    (2, 219, "Backup heating start accumulation", None, None, False),
    (2, 223, "Backup DHW temperature reading interval", "min", "duration", False),
    (2, 231, "DHW setpoint", "°C", "temperature", False),
    (2, 235, "DHW restart delta", "°C", "temperature", False),
    (2, 243, "DHW priority shift start temperature", "°C", "temperature", False),
    (2, 247, "DHW minimum working time", "min", "duration", False),
    (2, 251, "Heating maximum working time", "min", "duration", False),
    (2, 255, "Heating allowable temperature drift", "°C", "temperature", False),
    (2, 263, "DHW storage enabled raw", None, None, False),
    (2, 267, "DHW reheating enabled raw", None, None, False),
    (2, 271, "DHW reheat setpoint", "°C", "temperature", False),
    (2, 275, "DHW reheat restart delta", "°C", "temperature", False),
    (2, 279, "Circuit 2 enabled raw", None, None, False),
    (2, 283, "Circuit 2 cooling setpoint", "°C", "temperature", False),
    (2, 287, "Circuit 2 heating curve raw", None, None, False),
    (2, 291, "Circuit 2 water curve point 1", "°C", "temperature", False),
    (2, 295, "Circuit 2 water curve point 2", "°C", "temperature", False),
    (2, 299, "Circuit 2 water curve point 3", "°C", "temperature", False),
    (2, 303, "Circuit 2 water curve point 4", "°C", "temperature", False),
    (2, 307, "Circuit 2 water curve point 5", "°C", "temperature", False),
    (2, 311, "Circuit 2 heating setpoint", "°C", "temperature", False),
    (2, 323, "Reduced setpoint enabled raw", None, None, False),
    (2, 327, "Reduced setpoint temperature delta", "°C", "temperature", False),
    (2, 331, "Quiet operation enabled raw", None, None, False),
    (2, 335, "Reduced setpoint allowable drift", "°C", "temperature", False),
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
        if device_class == "enum":
            self._attr_options = list(OPERATING_MODES.values())
        if self.kind == 1 and self.offset in (183, 187, 191):
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif unit and self.kind == 1 and self.offset != 163:
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
        if value is not None and self.kind == 1 and self.offset == 171:
            return decode_operating_mode(value)
        return round(value, 2) if value is not None else None
