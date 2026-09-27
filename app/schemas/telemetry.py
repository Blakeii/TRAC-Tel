from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TelemetryCreate(BaseModel):
    terminal_id: str = Field(..., example="AML-001")
    raw_ussd_response: Optional[str] = Field(None, example="Solde: 0.00 DA, Internet: 4.5 Go...")
    parsed_balance_mb: Optional[float] = Field(None, example=4608.0)
    battery_level: Optional[int] = Field(None, example=85)
    battery_temp_c: Optional[float] = Field(None, example=36.4)
    signal_strength_dbm: Optional[int] = Field(None, example=-85)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

class TelemetryResponse(TelemetryCreate):
    id: int
    received_at: datetime

    class Config:
        from_attributes = True