"""The Smart Bed integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from .smart_bed_device import SmartBedDevice
from .models import SmartBedData

from homeassistant.core import callback
from homeassistant.components import bluetooth
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from bleak_retry_connector import close_stale_connections_by_address

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry) -> bool:
    """Set up Smart Bed device from config entry."""
    address = entry.unique_id

    assert address is not None
    await close_stale_connections_by_address(address)
    
    ble_device = bluetooth.async_ble_device_from_address(hass, address)

    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find Smart Bed device with address {address}")

    smart_bed = SmartBedDevice(_LOGGER, ble_device)

    @callback
    async def _async_update_method() -> None:
        """Update the device state."""
        try:
            await smart_bed.update_device_data()
        except Exception as err:
            raise UpdateFailed(f"Unable to fetch data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_method,
        update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = SmartBedData(smart_bed, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
