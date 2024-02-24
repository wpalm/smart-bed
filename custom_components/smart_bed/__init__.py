"""The Smart Bed integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from .smart_bed_ble import SmartBedDevice

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import METRIC_SYSTEM
from bleak_retry_connector import close_stale_connections_by_address

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

PLATFORMS: list[str] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Bed device from config entry."""
    hass.data.setdefault(DOMAIN, {})
    address = entry.unique_id

    assert address is not None
    await close_stale_connections_by_address(address)
    
    ble_device = bluetooth.async_ble_device_from_address(hass, address)

    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find Smart Bed device with address {address}")

    async def _async_update_method() -> SmartBedDevice:
        ble_device = bluetooth.async_ble_device_from_address(hass, address)
        smart_bed = SmartBedDevice(_LOGGER, ble_device)

        try:
            await smart_bed.update_device_data()
        except Exception as err:
            raise UpdateFailed(f"Unable to fetch data: {err}") from err

        return smart_bed

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_method,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
