from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ScannerBase(BaseModel):
    identifier: str
    name: str

class ScannerCreate(ScannerBase):
    pass

class ScannerUpdate(BaseModel):
    name: Optional[str] = None

class ScannerResponse(ScannerBase):
    id: int
    last_seen: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
