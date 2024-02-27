"""Platform for sensor integration."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .const import DOMAIN
from .coordinator import SmartBedCoordinator
from .smart_bed_device import SmartBedDevice


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
        ) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator: SmartBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        PositionHeadSensor(coordinator),
        PositionLegsSensor(coordinator),
    ])


class SensorBase(CoordinatorEntity[SmartBedCoordinator], SensorEntity):
    def __init__(self, 
                 coordinator: SmartBedCoordinator
                ) -> None:
        super().__init__(coordinator)
        self._device: SmartBedDevice = coordinator.api

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.identifier)}}
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.sensors[self._device.identifier]


class PositionHeadSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:head"

    def __init__(self, 
                 coordinator: DataUpdateCoordinator[None], 
                 device: SmartBedDevice,
                 ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device.identifier}_position_head"
        self._attr_name = f"{self._device.name} Position Head"
        self._state = None


class PositionLegsSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:foot-print"

    def __init__(self,
                 coordinator: DataUpdateCoordinator[None],
                 device: SmartBedDevice,
                 ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device.identifier}_position_legs"
        self._attr_name = f"{self._device.name} Position Legs"
        self._state = None
