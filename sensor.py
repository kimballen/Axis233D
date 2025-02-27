from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    axis = hass.data[DOMAIN][config_entry.entry_id]["axis"]
    
    sensors = []
    for port in range(1, 5):  # 4 input ports
        sensors.append(Axis233DInputSensor(coordinator, axis, port))
    
    async_add_entities(sensors, True)

class Axis233DInputSensor(CoordinatorEntity, SensorEntity):
    """Input sensor for Axis camera."""

    def __init__(self, coordinator, axis, port_number):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._axis = axis
        self._port = port_number
        self._attr_name = f"Axis Input {self._port}"
        self._attr_unique_id = f"{self._axis.ip_address}_input_{self._port}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data["status"]:
            return None
            
        status_text = self.coordinator.data["status"]
        for line in status_text.split('\n'):
            if f"Input {self._port}:" in line:
                return STATE_ON if "ON" in line else STATE_OFF
        return None
