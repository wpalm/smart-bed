"""Platform for button integration."""
from __future__ import annotations
import logging
from .smart_bed_device import SmartBedDevice
from .models import SmartBedData
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO: Add all supported commands

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    data: SmartBedData = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        StartWaveButton(data.device)
    ])

class ButtonBase(ButtonEntity):
    def __init__(self, device: SmartBedDevice):
        self._device = device

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.identifier)}}

class StartWaveButton(ButtonBase):
    def __init__(self, device: SmartBedDevice):
        super().__init__(device)
        self._attr_unique_id = f"{self._device.identifier}_start_wave_button"
        self._attr_name = f"{self._device.name} Start Wave Button"

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.send_command_wave()