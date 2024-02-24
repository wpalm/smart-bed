"""Smart Bed BLE devices"""

from __future__ import annotations

import asyncio
import dataclasses
import logging

from typing import Any, Callable, TypeVar

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


class SmartBedDevice:
    """Smart Bed device."""
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
    __ble_device: BLEDevice
    __motor_status_data: bytearray | None = None
    __event: asyncio.Event

    def __init__(self, logger: Logger, ble_device: BLEDevice):
        super().__init__()
        self.logger = logger
        self.__event = asyncio.Event()
        self.__ble_device = ble_device

    # TODO: Get real position values
    async def __update_position_head(self, client: BleakClient):
        self.__event = asyncio.Event()
        try:
            self.__motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC_UUID_READ)
        except:
            self.logger.warn("_get_position_head Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self.__event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting data.")
        except:
            self.logger.warn("_get_position_head Bleak error 2")

        if self.__motor_status_data is not None and len(self.__motor_status_data) == 1:
            self.sensors["position_head"] = int(self._motor__status_data[0])
        else:
            self.sensors["position_head"] = None


    # TODO: Get real position values
    async def __update_position_feet(self, client: BleakClient):
        self.__event = asyncio.Event()
        try:
            self.__motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC_UUID_READ)
        except:
            self.logger.warn("_get_position_feet Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self.__event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting data.")
        except:
            self.logger.warn("_get_position_feet Bleak error 2")

        if self.__motor_status_data is not None and len(self.__motor_status_data) == 1:
            self.sensors["position_feet"] = int(self.__motor_status_data[0])
        else:
            self.sensors["position_feet"] = None


    async def update_device_data(self):
        """Update the device data."""
        client = await establish_connection(BleakClient, self.__ble_device, self.__ble_device.address)
        
        self.name = self.__ble_device.name
        self.address = self.__ble_device.address

        await self.__update_position_head(client)
        await self.__update_position_feet(client)

        await client.disconnect()
    
    
    async def __send_motor_command(self, client: BleakClient, command, duration):
        delay = 0.1
        repeat = duration/delay
        for _ in range(int(repeat)):
            await client.write_gatt_char(MOTOR_COMMAND_CHARACTERISTIC_UUID_WRITE, data=command)
            await asyncio.sleep(delay)


    async def send_command_head_up(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_HEAD_UP, 20 if (max) else duration)
    

    async def send_command_head_down(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_HEAD_DOWN, 20 if (max) else duration)
    

    async def send_command_feet_up(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_FEET_UP, 20 if (max) else duration)
    

    async def send_command_feet_down(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_FEET_DOWN, 20 if (max) else duration)
    

    async def send_command_up(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_UP, 20 if (max) else duration)
    

    async def send_command_down(self, client: BleakClient, duration = 0.2, max = False):
        await self.__send_motor_command(MOTOR_COMMAND_VALUE_DOWN, 20 if (max) else duration)
    

    async def send_command_wave(self, client: BleakClient, repeat = 1):
        for _ in range(repeat):
            await self._send_command_up(client, device, max=True)
            await self._send_command_down(client, device, max=True)
