from sqlalchemy.orm import Session
from ..cards.models import AccessLog, Card

def get_access_logs(db: Session, limit: int = 50):
    return db.query(
        AccessLog.id,
        AccessLog.uid,
        AccessLog.status,
        AccessLog.timestamp,
        Card.name.label("person_name")
    ).outerjoin(
        Card, AccessLog.uid == Card.uid
    ).order_by(AccessLog.timestamp.desc()).limit(limit).all()

def get_access_summary(db: Session):
    total = db.query(AccessLog).count()
    unknowns = db.query(AccessLog).filter(AccessLog.status == "unknown").count()
    return {"total_scans": total, "unknown_scans": unknowns}
