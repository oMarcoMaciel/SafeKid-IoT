from sqlalchemy import Column, Integer, String, DateTime, func
from ...core.database import Base

class TrackingLog(Base):
    __tablename__ = "tracking_logs"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, index=True, nullable=False)
    rssi = Column(Integer, nullable=False)
    zone = Column(String, nullable=False) # "Very Near", "Near", "Far"
    scanner = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
