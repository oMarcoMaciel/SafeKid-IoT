from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.mqtt_client import mqtt_client
from . import service

router = APIRouter(prefix="/api/tracking", tags=["tracking"])

@router.get("/discovery", response_model=Dict[str, dict])
def get_discovered_tags():
    """Returns recently discovered MAC addresses (last 1 min)"""
    return mqtt_client.discovered_tags

@router.get("/live")
def get_live_tracking(db: Session = Depends(get_db)):
    """Returns the current location status of all students with trackers"""
    return service.get_live_tracking(db)

@router.get("/heatmap/{mac}")
def get_heatmap_data(mac: str, db: Session = Depends(get_db)):
    """Returns structured data for stacked bar charts per scanner"""
    return service.get_heatmap_data(db, mac)
