"""Smart Bed device."""

from __future__ import annotations
import asyncio
from logging import Logger
from .const import (
    MANUFACTURER_NAME_STRING_CHARACTERISTIC,
    MODEL_NUMBER_STRING_CHARACTERISTIC,
    FIRMWARE_REVISION_STRING_CHARACTERISTIC,
    SOFTWARE_REVISION_STRING_CHARACTERISTIC,
    MOTOR_COMMAND_CHARACTERISTIC,
    FLOOR_LIGHT_CHARACTERISTIC,
    FACTORY_RESET_CHARACTERISTIC,
    MOTOR_STATUS_CHARACTERISTIC,
    CHIP_TEMP_CHARACTERISTIC,
    SERVICE_IF_CHARACTERISTIC,
    MOTOR_COMMAND_DOWN,
    MOTOR_COMMAND_UP,
    MOTOR_COMMAND_RANGE_DURATION,
    MOTOR_COMMAND_HEAD_DOWN,
    MOTOR_COMMAND_HEAD_UP,
    MOTOR_COMMAND_HEAD_RANGE_DURATION,
    MOTOR_COMMAND_LEGS_DOWN,
    MOTOR_COMMAND_LEGS_UP,
    MOTOR_COMMAND_LEGS_RANGE_DURATION,
)
from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice


class BleakCharacteristicMissing(BleakError):
    """Raised when a characteristic is missing from a service."""


class BleakServiceMissing(BleakError):
    """Raised when a service is missing."""


class SmartBedDevice:
    """Smart Bed device."""
    hw_version: str = ""
    sw_version: str = ""
    model: str = ""
    manufacturer: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    __event: asyncio.Event
    __ble_device: BLEDevice

    __motor_status_data: bytearray | None = None
    position_head_pct: int | None = None
    position_legs_pct: int | None = None

    def __init__(self, logger: Logger, ble_device: BLEDevice):
        super().__init__()
        self.logger = logger
        self.__event = asyncio.Event()
        self.__ble_device = ble_device

    # TODO: Get real position values
    async def __update_position_head(self, client: BleakClient):
        self.__event = asyncio.Event()
        try:
            self.__motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC)
        except:
            self.logger.warn("_get_position_head Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self.__event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting position_head data.")
        except:
            self.logger.warn("_get_position_head Bleak error 2")

        if self.__motor_status_data is not None and len(self.__motor_status_data) == 1:
            self.position_head_pct = int(self._motor__status_data[0])
        else:
            self.position_head_pct = None


    # TODO: Get real position values
    async def __update_position_legs(self, client: BleakClient):
        self.__event = asyncio.Event()
        try:
            self.__motor_status_data = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC)
        except:
            self.logger.warn("_get_position_legs Bleak error 1")

        # Wait for up to 5 seconds to see if a callback comes in.
        try:
            await asyncio.wait_for(self.__event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting position_legs data.")
        except:
            self.logger.warn("_get_position_legs Bleak error 2")

        if self.__motor_status_data is not None and len(self.__motor_status_data) == 1:
            self.position_legs_pct = int(self.__motor_status_data[0])
        else:
            self.position_legs_pct = None


    async def update_device_data(self):
        """Update the device data."""
        async with BleakClient(self.__ble_device) as client:
            self.name = self.__ble_device.name
            self.address = self.__ble_device.address
            self.identifier = self.__ble_device.address

            await self.__update_position_head(client)
            await self.__update_position_legs(client)
    
    
    async def __send_motor_command(self, command, duration):
        async with BleakClient(self.__ble_device) as client:
            delay: float = 0.1
            repeat: int = int(duration / delay)
            for _ in range(repeat):
                await client.write_gatt_char(MOTOR_COMMAND_CHARACTERISTIC, data=command)
                await asyncio.sleep(delay)


    async def down(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_DOWN, MOTOR_COMMAND_RANGE_DURATION if max else duration)


    async def up(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_UP, MOTOR_COMMAND_RANGE_DURATION if max else duration)


    async def head_down(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_HEAD_DOWN, MOTOR_COMMAND_HEAD_RANGE_DURATION if max else duration)


    async def head_up(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_HEAD_UP, MOTOR_COMMAND_HEAD_RANGE_DURATION if max else duration)


    async def legs_down(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_LEGS_DOWN, MOTOR_COMMAND_LEGS_RANGE_DURATION if max else duration)


    async def legs_up(self, duration=0.2, max=False):
        await self.__send_motor_command(MOTOR_COMMAND_LEGS_UP, MOTOR_COMMAND_LEGS_RANGE_DURATION if max else duration)


    async def start_wave(self, repeat=2):
        for _ in range(repeat):
            await self.up(max=True)
            await self.down(max=True)
