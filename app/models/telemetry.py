from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    terminal_id = Column(String, ForeignKey("terminals.id", ondelete="CASCADE"), nullable=False)
    
    raw_ussd_response = Column(String, nullable=True)
    parsed_balance_mb = Column(Float, nullable=True)
    battery_level = Column(Integer, nullable=True)
    battery_temp_c = Column(Float, nullable=True)
    signal_strength_dbm = Column(Integer, nullable=True)
    
    recorded_at = Column(DateTime, nullable=False)        # Timestamp on tablet
    received_at = Column(DateTime, default=datetime.utcnow) # Server ingestion time

    terminal = relationship("Terminal", back_populates="telemetry_logs")

# Composite Index for fast queries by terminal and time
Index("idx_telemetry_terminal_date", TelemetryLog.terminal_id, TelemetryLog.recorded_at)