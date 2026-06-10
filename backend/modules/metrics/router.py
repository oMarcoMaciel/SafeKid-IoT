from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from . import service, schemas
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/logs", response_model=schemas.PaginatedAccessLogs)
def get_logs(
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return service.get_access_logs(db, skip=skip, limit=limit, start_date=start_date, end_date=end_date)

@router.get("/summary", response_model=schemas.SummaryResponse)
def get_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return service.get_access_summary(db, start_date=start_date, end_date=end_date)
