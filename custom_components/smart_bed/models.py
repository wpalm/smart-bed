"""The Smart Bed integration models."""
from __future__ import annotations
from dataclasses import dataclass
from .smart_bed_device import SmartBedDevice
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


@dataclass
class SmartBedData:
    """Data for the Smart Bed integration."""

    device: SmartBedDevice
    coordinator: DataUpdateCoordinator[None]