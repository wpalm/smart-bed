"""Platform for button integration."""
from __future__ import annotations
import logging
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
from .smart_bed_device import SmartBedDevice
from .coordinator import SmartBedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator: SmartBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        StartWaveButton(coordinator.api)
    ])


class ButtonBase(ButtonEntity):
    def __init__(self, device: SmartBedDevice):
        self._device = device

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.identifier)}}


class DownButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_down_button"
        self._attr_name = f"{self._device.name} Down Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.down()


class UpButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_up_button"
        self._attr_name = f"{self._device.name} Up Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.up()


class HeadDownButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_head_down_button"
        self._attr_name = f"{self._device.name} Head Down Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.head_down()


class HeadUpButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_head_up_button"
        self._attr_name = f"{self._device.name} Head Up Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.head_up()


class LegsDownButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_legs_down_button"
        self._attr_name = f"{self._device.name} Legs Down Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.legs_down()


class LegsUpButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_legs_up_button"
        self._attr_name = f"{self._device.name} Legs Up Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.legs_up()
        
class StartWaveButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_start_wave_button"
        self._attr_name = f"{self._device.name} Start Wave Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.start_wave()
