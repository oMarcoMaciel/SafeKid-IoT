from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TrackingLogResponse(BaseModel):
    id: int
    mac: str
    rssi: int
    zone: str
    scanner: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
