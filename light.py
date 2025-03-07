from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

_LOGGER = logging.getLogger(__name__)

# Constants
DOMAIN = "wohnzimmer_deckenleuchte_rgb"

async def async_setup_platform(
    hass: HomeAssistant, config: dict, async_add_entities: AddEntitiesCallback, discovery_info=None
):
    """Set up the remote-controlled light platform."""
    name = config.get("name", "Wohnzimmer Deckenleuchte RGB")
    entity = MyRemoteLight(hass, name)
    _LOGGER.info("Adding entity: %s", entity.name)
    async_add_entities([entity], True)


class MyRemoteLight(LightEntity):
    """Representation of the remote-controlled light."""

    def __init__(self, hass: HomeAssistant, name: str):
        """Initialize the light."""
        self._hass = hass
        self._name = name
        self._is_on = False
        self._color = None
        self._matched_color = None

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the light."""
        return self._is_on

    @property
    def hs_color(self):
        """Return the current HS color of the light."""
        return self._color

    @property
    def rgb_color(self):
        """Return the current RGB color of the light."""
        if self._color:
            hue, sat = self._color
            return self._hs_to_rgb(hue, sat)
        return None

    @property
    def rgbw_color(self):
        """Return the current RGBW color of the light."""
        if self._color:
            hue, sat = self._color
            rgb = self._hs_to_rgb(hue, sat)
            white = 255 if sat < 10 else 0  # White component based on saturation
            return (*rgb, white)
        return None

    @property
    def rgbww_color(self):
        """Return the current RGBWW color of the light."""
        if self._color:
            hue, sat = self._color
            rgb = self._hs_to_rgb(hue, sat)
            warm_white = 255 if sat < 10 and hue < 50 else 0
            cool_white = 255 if sat < 10 and hue >= 50 else 0
            return (*rgb, warm_white, cool_white)
        return None

    @property
    def xy_color(self):
        """Return the current XY color of the light."""
        if self._color:
            hue, sat = self._color
            return self._hs_to_xy(hue, sat)
        return None

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return 255 if self._is_on else None

    def _hs_to_rgb(self, hue, saturation):
        """Convert HS to RGB."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, saturation / 100.0, 1.0)
        return int(r * 255), int(g * 255), int(b * 255)

    def _hs_to_xy(self, hue, saturation):
        """Convert HS to XY."""
        rgb = self._hs_to_rgb(hue, saturation)
        r, g, b = [x / 255.0 for x in rgb]
        # Apply a gamma correction to the RGB values
        r = (r + 0.055) / 1.055 ** 2.4 if r > 0.04045 else r / 12.92
        g = (g + 0.055) / 1.055 ** 2.4 if g > 0.04045 else g / 12.92
        b = (b + 0.055) / 1.055 ** 2.4 if b > 0.04045 else b / 12.92
        # Convert RGB to XYZ
        X = r * 0.4124 + g * 0.3576 + b * 0.1805
        Y = r * 0.2126 + g * 0.7152 + b * 0.0722
        Z = r * 0.0193 + g * 0.1192 + b * 0.9505
        # Convert XYZ to xy
        xy = (X / (X + Y + Z), Y / (X + Y + Z)) if (X + Y + Z) != 0 else (0, 0)
        return xy

    def _match_color(self, color):
        """Match the given HS color to a predefined color."""
        if color is None:
            _LOGGER.debug("No color provided; defaulting to white.")
            return "white"

        hue, saturation = color
        _LOGGER.debug("Matching color: Hue=%s, Saturation=%s", hue, saturation)

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
            color = kwargs["hs_color"]
            self._color = color  # Store the actual HS tuple
            self._matched_color = self._match_color(color)  # Store the matched color string

            _LOGGER.info("Turn on called with color: %s, matched color: %s", color, self._matched_color)

            if self._matched_color == "white":
                await self._hass.services.async_call(
                    "script", "wohnzimmer_deckenleuchte_rgb_white", blocking=True
                )
            elif self._matched_color == "red":
                await self._hass.services.async_call(
                    "script", "wohnzimmer_deckenleuchte_rgb_rot", blocking=True
                )
            elif self._matched_color == "green":
                await self._hass.services.async_call(
                    "script", "wohnzimmer_deckenleuchte_rgb_grun", blocking=True
                )
            elif self._matched_color == "blue":
                await self._hass.services.async_call(
                    "script", "wohnzimmer_deckenleuchte_rgb_blau", blocking=True
                )
            else:
                _LOGGER.warning("No matching color found for: %s", color)
                self._color = (0, 0)  # Default to white in HS
                self._matched_color = "white"

        else:  # Default action: turn on white
            _LOGGER.info("Turn on called without color; defaulting to white.")
            await self._hass.services.async_call(
                "script", "wohnzimmer_deckenleuchte_rgb_turn_on", blocking=True
            )
            self._color = (0, 0)  # Default to white in HS
            self._matched_color = "white"

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the light."""
        self._is_on = False
        self._color = None
        await self._hass.services.async_call(
            "script", "wohnzimmer_deckenleuchte_rgb_switch", blocking=True
        )
        self.async_write_ha_state()

    @property
    def supported_color_modes(self):
        """Return the supported color modes."""
        return {ColorMode.HS}

    @property
    def color_mode(self):
        """Return the current color mode."""
        return ColorMode.HS if self._color else None

    @property
    def unique_id(self):
        """Return a unique ID for the entity."""
        return f"{self._name.lower().replace(' ', '_')}_light"