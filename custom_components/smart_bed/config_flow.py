from __future__ import annotations

import logging
from typing import Any

from .smart_bed_ble import SmartBedDevice
from bleak import BleakError
import voluptuous as vol

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothServiceInfo,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartBedDeviceError(Exception):
    """Error to indicate a device update failed."""

# TODO: Add notice about the need to have the Smart Bed in pairing mode, await until user confirms the device is in pairing mode
class SmartBedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Bed."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._discovered_devices: dict[str, SmartBedDevice] = {}

    async def _get_device_data(self, discovery_info: BluetoothServiceInfo) -> SmartBedDevice:
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, discovery_info.address)
        if ble_device is None:
            _LOGGER.debug("no ble_device in _get_device_data")
            raise SmartBedDeviceError("No ble_device")

        smart_bed = SmartBedDevice(_LOGGER)

        try:
            await smart_bed.update_device_data(ble_device)
        except BleakError as err:
            _LOGGER.error(
                "Error connecting to and getting data from %s: %s",
                discovery_info.address,
                err,
            )
            raise SmartBedDeviceError("Failed getting device data") from err
        except Exception as err:
            _LOGGER.error(
                "Unknown error occurred from %s: %s", discovery_info.address, err
            )
            raise err
        return smart_bed

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfo) -> FlowResult:
        """Handle a flow initialized by discovery over Bluetooth."""
        _LOGGER.debug("Discovered BT device: %s", discovery_info)
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        try:
            device = await self._get_device_data(discovery_info)
        except SmartBedDeviceError:
            return self.async_abort(reason="cannot_connect")
        except Exception:
            return self.async_abort(reason="unknown")

        self.context["title_placeholders"] = {"name": device.name}

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the Bluetooth confirmation step."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.context["title_placeholders"]["name"], data={}
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            device = self._discovered_devices[address]

            self.context["title_placeholders"] = {
                "name": device.name,
            }

            return self.async_create_entry(title=device.name, data={})

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue

            if discovery_info.advertisement.local_name is None:
                continue

            if not discovery_info.manufacturer_id == 944:
                continue

            _LOGGER.debug("Found Smart Bed device")
            _LOGGER.debug("Smart Bed address: %s", address)
            _LOGGER.debug("Smart Bed manufacturer data: %s", discovery_info.manufacturer_data)
            _LOGGER.debug("Smart Bed advertisement: %s", discovery_info.advertisement)
            _LOGGER.debug("Smart Bed device: %s", discovery_info.device)
            _LOGGER.debug("Smart Bed service data: %s", discovery_info.service_data)
            _LOGGER.debug("Smart Bed service uuids: %s", discovery_info.service_uuids)
            _LOGGER.debug("Smart Bed rssi: %s", discovery_info.rssi)
            _LOGGER.debug("Smart Bed local name: %s", discovery_info.advertisement.local_name)
            try:
                device = await self._get_device_data(discovery_info)
            except SmartBedDeviceError:
                return self.async_abort(reason="cannot_connect")
            except Exception:
                return self.async_abort(reason="unknown")
            self._discovered_devices[address] = device

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        titles = {
            address: device.name
            for (address, device) in self._discovered_devices.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(titles),
                },
            ),
        )