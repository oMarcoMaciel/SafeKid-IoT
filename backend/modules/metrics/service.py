from sqlalchemy.orm import Session
from sqlalchemy import func
from ..cards.models import AccessLog, Card
from datetime import datetime
from typing import Optional

def get_access_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
):
    query = db.query(
        AccessLog.id,
        AccessLog.uid,
        AccessLog.status,
        AccessLog.timestamp,
        Card.name.label("person_name")
    ).outerjoin(
        Card, AccessLog.uid == Card.uid
    )

    if start_date:
        query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AccessLog.timestamp <= end_date)

    total = query.count()
    items = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total
    }

def get_access_summary(
    db: Session,
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
):
    total_query = db.query(AccessLog)
    unknowns_query = db.query(AccessLog).filter(AccessLog.status == "unknown")

    if start_date:
        total_query = total_query.filter(AccessLog.timestamp >= start_date)
        unknowns_query = unknowns_query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        total_query = total_query.filter(AccessLog.timestamp <= end_date)
        unknowns_query = unknowns_query.filter(AccessLog.timestamp <= end_date)

    total = total_query.count()
    unknowns = unknowns_query.count()
    
    return {"total_scans": total, "unknown_scans": unknowns}
