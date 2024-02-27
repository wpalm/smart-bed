import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import async_timeout
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .smart_bed_device import SmartBedDevice

_LOGGER = logging.getLogger(__name__)


class SmartBedCoordinator(DataUpdateCoordinator):
    """ Smart Bed data update coordinator. """
    def __init__(self, hass, api: SmartBedDevice):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(20):
                return await self.api.update_device_data()
        except Exception as err:
            raise UpdateFailed(f"Unable to fetch data: {err}")