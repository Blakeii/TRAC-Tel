from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TerminalBase(BaseModel):
    gate_name: str = Field(..., example="Gate A - Main Entry")
    location_desc: Optional[str] = Field(None, example="West Laydown Yard")
    sim_phone_number: Optional[str] = Field(None, example="0550123456")
    total_quota_mb: int = Field(10240, example=10240)
    active_ussd_code: str = Field("*200#", example="*200#")
    poll_interval_hours: int = Field(6, example=6)

class TerminalCreate(TerminalBase):
    id: str = Field(..., example="AML-001")

class TerminalUpdate(BaseModel):
    gate_name: Optional[str] = None
    location_desc: Optional[str] = None
    sim_phone_number: Optional[str] = None
    total_quota_mb: Optional[int] = None
    active_ussd_code: Optional[str] = None
    poll_interval_hours: Optional[int] = None

class TerminalResponse(TerminalBase):
    id: str
    created_at: datetime
    updated_at: datetime
    latest_balance_mb: Optional[float] = None
    latest_battery_level: Optional[int] = None
    latest_battery_temp_c: Optional[float] = None
    latest_signal_dbm: Optional[int] = None
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True

# Lightweight schema returned when tablet queries its dynamic config
class TerminalConfigResponse(BaseModel):
    terminal_id: str
    active_ussd_code: str
    poll_interval_hours: int