from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ..cards.schemas import AccessLogResponse
from . import service
from typing import List

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/logs", response_model=List[AccessLogResponse])
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    return service.get_access_logs(db, limit)

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return service.get_access_summary(db)
