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


class StartWaveButton(ButtonEntity):
    def __init__(self, device: SmartBedDevice):
        self._device = device

    async def async_press(self) -> None:
        _LOGGER.debug("Pressed button")
        await self._device.send_command_wave()