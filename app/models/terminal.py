from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Terminal(Base):
    __tablename__ = "terminals"

    id = Column(String, primary_key=True, index=True)  # e.g., 'AML-001'
    gate_name = Column(String, nullable=False)          # e.g., 'Gate A - Main Entry'
    location_desc = Column(String, nullable=True)       # e.g., 'West Laydown Yard'
    sim_phone_number = Column(String, nullable=True)    # e.g., '0550123456'
    total_quota_mb = Column(Integer, default=10240)     # Default 10 GB
    active_ussd_code = Column(String, default="*200#")  # Dynamic USSD string
    poll_interval_hours = Column(Integer, default=6)    # Default polling period
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-Many Relationship with Telemetry Logs
    telemetry_logs = relationship("TelemetryLog", back_populates="terminal", cascade="all, delete-orphan")