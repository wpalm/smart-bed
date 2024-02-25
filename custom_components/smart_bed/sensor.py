"""Platform for sensor integration."""
from __future__ import annotations

import logging

from .smart_bed_device import SmartBedDevice

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass
)
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator: DataUpdateCoordinator[SmartBedDevice] = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        PositionHeadSensor(coordinator.data),
        PositionLegsSensor(coordinator.data)
    ])

# TODO: add _handle_coordinator_update callback to support polling?
class SensorBase(SensorEntity):
    def __init__(self, device: SmartBedDevice):
        self._device = device

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.identifier)}}


class PositionHeadSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:head"

    def __init__(self, device: SmartBedDevice):
        """Initialize the sensor."""
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_position_head"
        self._attr_name = f"{self._device.name} Position Head"
        self._state = None


class PositionLegsSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:foot-print"

    def __init__(self, device: SmartBedDevice):
        """Initialize the sensor."""
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_position_legs"
        self._attr_name = f"{self._device.name} Position Legs"
        self._state = None
