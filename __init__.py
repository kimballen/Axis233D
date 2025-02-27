from datetime import timedelta
import logging
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, PLATFORMS, DEFAULT_SCAN_INTERVAL
from .axis_io import Axis233DIO

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Axis 233D from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API instance
    axis = Axis233DIO(
        entry.data[CONF_HOST],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        http_port=entry.data.get("http_port", 80),
    )

    async def async_update_data():
        """Fetch data from API."""
        try:
            # Test connection and get initial data
            if not axis.connected and not await hass.async_add_executor_job(axis.test_connection):
                raise UpdateFailed("Failed to connect to camera")
            
            # Get all ports status
            status = await hass.async_add_executor_job(axis.get_all_ports)
            if status is None:
                raise UpdateFailed("Failed to get port status")
                
            return {"status": status}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Axis {entry.data[CONF_HOST]}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "axis": axis
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
