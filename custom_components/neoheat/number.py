"""Confirmed Circuit 1 temperature control."""
from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([NeoheatCircuit1Setpoint(entry)])


class NeoheatCircuit1Setpoint(CoordinatorEntity, NumberEntity):
    """Heating setpoint when Circuit 1 heating curve is disabled."""

    _attr_has_entity_name = True
    _attr_name = "Circuit 1 heating setpoint"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 15
    _attr_native_max_value = 55
    _attr_native_step = 1

    def __init__(self, entry):
        super().__init__(entry.runtime_data)
        self._attr_unique_id = f"{entry.entry_id}_circuit1_heating_setpoint"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name="Neoheat",
            manufacturer="Neoheat", model="EKO II (experimental local protocol)",
        )

    @property
    def available(self):
        return super().available and 163 in (self.coordinator.data or {}).get(2, {})

    @property
    def native_value(self):
        value = (self.coordinator.data or {}).get(2, {}).get(163)
        return round(value, 1) if value is not None else None

    async def async_set_native_value(self, value):
        try:
            data = await self.coordinator.client.write_circuit1_setpoint(float(value))
        except (OSError, TimeoutError, ConnectionError) as error:
            raise HomeAssistantError("Neoheat did not confirm the new setpoint") from error
        self.coordinator.async_set_updated_data(data)
