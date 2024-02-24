"""Platform for sensor integration."""
from __future__ import annotations

import logging
import dataclasses

from .smart_bed_ble import SmartBedDevice

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSORS_MAPPING_TEMPLATE: dict[str, SensorEntityDescription] = {
    "position_head": SensorEntityDescription(
        key="position_head",
        name="Position Head",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:head",
    ),
    "position_feet": SensorEntityDescription(
        key="position_feet",
        name="Position Feet",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:foot-print",
    ),
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: DataUpdateCoordinator[SmartBedDevice] = hass.data[DOMAIN][entry.entry_id]

    entities = []
    _LOGGER.debug("got sensors: %s", coordinator.data.sensors)
    for sensor_type, sensor_value in coordinator.data.sensors.items():
        if sensor_type not in SENSORS_MAPPING_TEMPLATE:
            _LOGGER.debug(
                "Unknown sensor type detected: %s, %s",
                sensor_type,
                sensor_value,
            )
            continue
        entities.append(
            SmartBedSensor(coordinator, coordinator.data, SENSORS_MAPPING_TEMPLATE[sensor_type])
        )

    async_add_entities(entities)

class SmartBedSensor(CoordinatorEntity[DataUpdateCoordinator[SmartBedDevice]], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        smart_bed_device: SmartBedDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

        name = f"{smart_bed_device.name} {smart_bed_device.identifier}"

        self._attr_unique_id = f"{name}_{entity_description.key}"

        self._id = smart_bed_device.address
        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_BLUETOOTH,
                    smart_bed_device.address,
                )
            },
            name=name,
            manufacturer=smart_bed_device.manufacturer,
            model=smart_bed_device.model,
            hw_version=smart_bed_device.hw_version,
            sw_version=smart_bed_device.sw_version,
        )

    @property
    def native_value(self) -> StateType:
        try:
            return self.coordinator.data.sensors[self.entity_description.key]
        except KeyError:
            return None