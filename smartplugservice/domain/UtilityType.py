from enum import Enum

class UtilityType(str, Enum):
    """Supported utility types for SmartPlug."""
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"
    GAS = "GAS"