from enum import Enum

class SmartPlugStatus(str, Enum):
    """Operational status of a SmartPlug."""
    OFF = "off"
    ON = "on"