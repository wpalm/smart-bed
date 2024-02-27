"""Platform for sensor integration."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.const import PERCENTAGE, STATE_UNKNOWN, UnitOfTemperature
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
        MotorStatusSensor(coordinator),
        FloorLightSensor(coordinator),
        ChipTempSensor(coordinator),
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


class MotorStatusSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE  # TODO: Change to corrent unit
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, 
                 coordinator: SmartBedCoordinator, 
                 ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device.identifier}_motor_status"
        self._attr_name = f"{self._device.name} Motor Status"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._device.motor_status
    

class FloorLightSensor(SensorBase):
    _attr_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, 
                 coordinator: SmartBedCoordinator,
                 ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device.identifier}_floor_light"
        self._attr_name = f"{self._device.name} Floor Light"
        self._attr_device_class = "light"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._device.floor_light
    

class ChipTempSensor(SensorBase):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                coordinator: SmartBedCoordinator
                ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device.identifier}_chip_temp"
        self._attr_name = f"{self._device.name} Chip Temp"
        self.temperature = STATE_UNKNOWN

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._device.chip_temp