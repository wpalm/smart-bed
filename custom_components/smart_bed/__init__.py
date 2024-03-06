"""The Smart Bed integration."""
from __future__ import annotations
import logging
from homeassistant.components import bluetooth
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry
from .const import DOMAIN
from .smart_bed_device import SmartBedDevice
from .coordinator import SmartBedCoordinator

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry) -> bool:
    """Set up Smart Bed device from config entry."""
    address = entry.unique_id
    
    ble_device = bluetooth.async_ble_device_from_address(hass, address)
    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find Smart Bed device with address {address}")

    smart_bed = SmartBedDevice(_LOGGER, ble_device)

    # Get device data
    try:
        await smart_bed.update_device_data()
    except Exception as e:
        raise ConfigEntryNotReady(f"Could not get device data: {e}")

    # Register device in device registry
    dr = await device_registry.async_get_registry()
    await dr.async_get_or_create(
        config_entry_id=entry.entry_id,
        # TODO: Add more device metadata, connections={(dr.CONNECTION_NETWORK_MAC, config.mac)},
        identifiers={(DOMAIN, smart_bed.identifier)},
        manufacturer= smart_bed.manufacturer,
        name=smart_bed.name,
        model=smart_bed.model,
        sw_version= smart_bed.sw_version,
    )

    coordinator = SmartBedCoordinator(hass, smart_bed)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
