from pydantic import BaseModel, Field

from smartplugservice.domain.SmartPlugStatus import SmartPlugStatus
from smartplugservice.domain.UtilityType import UtilityType


class SmartPlug(BaseModel):
    id: str = Field(..., description="Slugified version of the name")
    name: str = Field(..., description="Unique human-readable identifier")
    utility_type: UtilityType = Field(..., description="Type of utility consumed")
    status: SmartPlugStatus = Field(default=SmartPlugStatus.OFF, description="Whether the node is active")
    real_time_consumption: float = Field(..., ge=0, description="Amount of utility consumed in real time")