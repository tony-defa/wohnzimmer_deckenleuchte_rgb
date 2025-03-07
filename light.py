from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up the light platform from a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    entity = MyRemoteLight(hass, config)
    async_add_entities([entity], True)


class MyRemoteLight(LightEntity):
    """Representation of the remote-controlled light."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the light."""
        self._hass = hass
        self._is_on = False
        self._color = None
        self._matched_color = None

        # Scripts from config
        self._on_script = config["on_script"]
        self._off_script = config["off_script"]
        self._white_script = config["white_script"]
        self._red_script = config["red_script"]
        self._green_script = config["green_script"]
        self._blue_script = config["blue_script"]

    @property
    def name(self):
        """Return the name of the light."""
        return "Wohnzimmer Deckenleuchte RGB"

    @property
    def is_on(self):
        """Return the state of the light."""
        return self._is_on

    @property
    def hs_color(self):
        """Return the current HS color of the light."""
        return self._color

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return 255 if self._is_on else None

    @property
    def supported_color_modes(self):
        """Return the supported color modes."""
        return {ColorMode.HS}

    @property
    def color_mode(self):
        """Return the current color mode."""
        return ColorMode.HS if self._color else None

    def _match_color(self, color):
        """Match the given HS color to a predefined color."""
        if color is None:
            return "white"

        hue, saturation = color
        if saturation < 10:  # Low saturation indicates white
            return "white"
        elif 0 <= hue < 30 or 330 <= hue <= 360:  # Red
            return "red"
        elif 90 <= hue <= 150:  # Green
            return "green"
        elif 210 <= hue <= 270:  # Blue
            return "blue"
        else:
            return None  # Unmatched color

    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        self._is_on = True

        if "hs_color" in kwargs:
            self._color = kwargs["hs_color"]
            self._matched_color = self._match_color(self._color)

            _LOGGER.info("Turn on called with color: %s, matched color: %s", self._color, self._matched_color)

            script_map = {
                "white": self._white_script,
                "red": self._red_script,
                "green": self._green_script,
                "blue": self._blue_script,
            }
            if self._matched_color in script_map:
                await self._hass.services.async_call(
                    "script", script_map[self._matched_color], blocking=True
                )
            else:
                _LOGGER.warning("No matching color found for: %s", self._color)
        else:
            # Default action: turn on with white color
            await self._hass.services.async_call(
                "script", self._on_script, blocking=True
            )
            self._color = (0, 0)  # Default to white in HS

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the light."""
        self._is_on = False
        self._color = None
        await self._hass.services.async_call(
            "script", self._off_script, blocking=True
        )
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID for the entity."""
        return "wohnzimmer_deckenleuchte_rgb_light"

