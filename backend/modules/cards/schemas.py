from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CardBase(BaseModel):
    uid: str
    name: str
    role: Optional[str] = "user"
    is_active: Optional[bool] = True
    tracker_mac: Optional[str] = None

class CardCreate(CardBase):
    pass

class CardUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    tracker_mac: Optional[str] = None

class CardResponse(CardBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccessLogResponse(BaseModel):
    id: int
    uid: str
    status: str
    timestamp: datetime
    person_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
