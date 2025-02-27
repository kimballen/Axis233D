from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switches."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    axis = hass.data[DOMAIN][config_entry.entry_id]["axis"]
    
    switches = []
    for port in range(1, 5):  # 4 output ports
        switches.append(Axis233DOutputSwitch(coordinator, axis, port))
    
    async_add_entities(switches, True)

class Axis233DOutputSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, axis, port_number):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._axis = axis
        self._port = port_number
        self._attr_name = f"Axis Output {self._port}"
        self._attr_unique_id = f"{self._axis.ip_address}_output_{self._port}"

    @property
    def is_on(self):
        """Return true if the output is on."""
        if not self.coordinator.data or not self.coordinator.data["status"]:
            return None
            
        status_text = self.coordinator.data["status"]
        for line in status_text.split('\n'):
            if f"Output {self._port}:" in line:
                return "ON" in line
        return None

    async def async_turn_on(self, **kwargs):
        """Turn the output on."""
        success = await self.hass.async_add_executor_job(
            self._axis.set_output_state, self._port, True
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the output off."""
        success = await self.hass.async_add_executor_job(
            self._axis.set_output_state, self._port, False
        )
        if success:
            await self.coordinator.async_request_refresh()
