"""Neoheat local read-only integration."""
import logging
from datetime import timedelta

from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import NeoheatClient
from .const import DOMAIN

LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


class NeoheatCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=timedelta(seconds=10))
        self.client = NeoheatClient(entry.data["host"], entry.data["port"])

    async def _async_update_data(self):
        try:
            return await self.client.read_snapshot()
        except (OSError, TimeoutError) as err:
            raise UpdateFailed("No valid Neoheat telemetry received") from err


async def async_setup_entry(hass, entry):
    coordinator = NeoheatCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        await coordinator.client.close()
        raise
    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.async_shutdown()
        await entry.runtime_data.client.close()
        return True
    return False

