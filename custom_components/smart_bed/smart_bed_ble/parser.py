"""Parser for Smart Bed BLE devices"""

from __future__ import annotations

import asyncio
import dataclasses
from collections import namedtuple
from datetime import datetime
import logging

from math import exp
from typing import Any, Callable, Tuple, TypeVar, cast

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])

class BleakCharacteristicMissing(BleakError):
    """Raised when a characteristic is missing from a service."""


class BleakServiceMissing(BleakError):
    """Raised when a service is missing."""


MOTOR_STATUS_CHARACTERISTIC_UUID_READ = "00001525-0000-1000-8000-00805f9b34fb"
MOTOR_COMMAND_CHARACTERISTIC_UUID_WRITE = "00001524-0000-1000-8000-00805f9b34fb"

# Full range: 20 s
MOTOR_COMMAND_VALUE_DOWN = b'\x00'
MOTOR_COMMAND_VALUE_UP = b'\x10'

# Full range: x s
MOTOR_COMMAND_VALUE_HEAD_UP = b'\x0B'
MOTOR_COMMAND_VALUE_HEAD_DOWN = b'\x0A'

# Full range: x s
MOTOR_COMMAND_VALUE_FEET_UP = b'\x09'
MOTOR_COMMAND_VALUE_FEET_DOWN = b'\x08'


_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class SmartBedDevice:
    """Response data with information about the Smart Bed device"""

    hw_version: str = ""
    sw_version: str = ""
    model: str = ""
    manufacturer: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )


class SmartBedBluetoothDeviceData:
    """Data for Smart Bed BLE sensors."""

    _motor_status_data: bytearray | None
    _event: asyncio.Event

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self._motor_status_data = None
        self._event = asyncio.Event()


    def disconnect_on_missing_services(func: WrapFuncType) -> WrapFuncType:
        """Define a wrapper to disconnect on missing services and characteristics.

        This must be placed after the retry_bluetooth_connection_error
        decorator.
        """

        async def _async_disconnect_on_missing_services_wrap(
            self, *args: Any, **kwargs: Any
        ) -> None:
            try:
                return await func(self, *args, **kwargs)
            except (BleakServiceMissing, BleakCharacteristicMissing) as ex:
                logger.warning(
                    "%s: Missing service or characteristic, disconnecting to force refetch of GATT services: %s",
                    self.name,
                    ex,
                )
                if self.client:
                    await self.client.clear_cache()
                    await self.client.disconnect()
                raise

        return cast(WrapFuncType, _async_disconnect_on_missing_services_wrap)

    # TODO: Get real position values
    @disconnect_on_missing_services
    async def _get_position_head(self, client: BleakClient, device: SmartBedDevice) -> SmartBedDevice:

        self._event = asyncio.Event()
        try:
            self._motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC_UUID_READ)
        except:
            self.logger.warn("_get_position_head Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self._event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting data.")
        except:
            self.logger.warn("_get_position_head Bleak error 2")

        if self._motor_status_data is not None and len(self._motor_status_data) == 1:
            device.sensors["position_head"] = int(self._motor_status_data[0])
        else:
            device.sensors["position_head"] = None

        self._motor_status_data = None
        return device

    # TODO: Get real position values
    @disconnect_on_missing_services
    async def _get_position_feet(self, client: BleakClient, device: SmartBedDevice) -> SmartBedDevice:

        self._event = asyncio.Event()
        try:
            self._motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC_UUID_READ)
        except:
            self.logger.warn("_get_position_head Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self._event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting data.")
        except:
            self.logger.warn("_get_position_head Bleak error 2")

        if self._motor_status_data is not None and len(self._motor_status_data) == 1:
            device.sensors["position_head"] = int(self._motor_status_data[0])
        else:
            device.sensors["position_head"] = None

        self._motor_status_data = None
        return device

    
    @disconnect_on_missing_services
    async def __send_motor_command(self, command, duration):
        delay = 0.1
        repeat = duration/delay
        for _ in range(int(repeat)):
            await self.__client.write_gatt_char(MOTOR_COMMAND_CHARACTERISTIC_UUID_WRITE, data=command)
            await asyncio.sleep(delay)


    async def _send_command_head_up(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_HEAD_UP, 20 if (max) else duration)
        return device
    

    async def _send_command_head_down(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_HEAD_DOWN, 20 if (max) else duration)
        return device
    

    async def _send_command_feet_up(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_FEET_UP, 20 if (max) else duration)
        return device
    

    async def _send_command_feet_down(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_FEET_DOWN, 20 if (max) else duration)
        return device
    

    async def _send_command_up(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_UP, 20 if (max) else duration)
        return device
    

    async def _send_command_down(self, client: BleakClient, device: SmartBedDevice, duration = 0.2, max = False) -> SmartBedDevice:
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_DOWN, 20 if (max) else duration)
        return device
    

    async def _send_command_wave(self, client: BleakClient, device: SmartBedDevice, repeat = 1) -> SmartBedDevice:
        for _ in range(repeat):
            await self._send_command_up(client, device, max=True)
            await self._send_command_down(client, device, max=True)
        return device


    async def update_device_data(self, ble_device: BLEDevice) -> SmartBedDevice:
        """Update the device data."""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        device = SmartBedDevice()
        device.name = ble_device.name
        device.address = ble_device.address

        device = await self._get_position_feet(client, device)
        device = await self._get_position_head(client, device)

        await client.disconnect()

        return device