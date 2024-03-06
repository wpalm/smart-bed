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
from bleak import BleakClient
from bleak.backends.device import BLEDevice


class SmartBedDevice:
    """Smart Bed device."""
    manufacturer: str = ""
    model: str = ""
    fw_version: str = ""
    sw_version: str = ""

    __ble_device: BLEDevice
    name: str = ""
    identifier: str = ""
    address: str = ""

    motor_status: bytearray | None = None
    floor_light: bytearray | None = None
    chip_temp: bytearray | None = None


    def __init__(self, logger: Logger, ble_device: BLEDevice):
        super().__init__()
        self.logger = logger
        self.__ble_device = ble_device


    async def update_device_data(self):
        """Update the device data."""
        async with BleakClient(self.__ble_device) as client:
            self.name = self.__ble_device.name
            self.address = self.__ble_device.address
            self.identifier = self.__ble_device.address

            # TODO: Get the device metadata
            # self.manufacturer = (await client.read_gatt_char(MANUFACTURER_NAME_STRING_CHARACTERISTIC)).decode("utf-8")
            # self.model = (await client.read_gatt_char(MODEL_NUMBER_STRING_CHARACTERISTIC)).decode("utf-8")
            # self.fw_version = (await client.read_gatt_char(FIRMWARE_REVISION_STRING_CHARACTERISTIC)).decode("utf-8")
            # self.sw_version = (await client.read_gatt_char(SOFTWARE_REVISION_STRING_CHARACTERISTIC)).decode("utf-8")

            self.motor_status = await client.read_gatt_char(MOTOR_STATUS_CHARACTERISTIC)
            self.floor_light = await client.read_gatt_char(FLOOR_LIGHT_CHARACTERISTIC)
            self.chip_temp = await client.read_gatt_char(CHIP_TEMP_CHARACTERISTIC)
    
    
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
