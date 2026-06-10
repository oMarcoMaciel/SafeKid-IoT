from sqlalchemy import Column, Integer, String, DateTime, func
from ...core.database import Base

class Scanner(Base):
    __tablename__ = "scanners"
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True, nullable=False) # ID técnico do ESP32
    name = Column(String, nullable=False)
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
