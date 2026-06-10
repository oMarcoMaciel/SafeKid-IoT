from pydantic import BaseModel
from typing import List, Optional
from ..cards.schemas import AccessLogResponse

class PaginatedAccessLogs(BaseModel):
    items: List[AccessLogResponse]
    total: int

class SummaryResponse(BaseModel):
    total_scans: int
    unknown_scans: int
