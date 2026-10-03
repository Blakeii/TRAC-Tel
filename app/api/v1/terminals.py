from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.terminal import Terminal
from app.models.telemetry import TelemetryLog
from app.schemas.terminal import (
    TerminalCreate,
    TerminalUpdate,
    TerminalResponse,
    TerminalConfigResponse
)
from app.schemas.telemetry import TelemetryResponse

router = APIRouter()

# --------------------------------------------------------------------------
# 1. List all terminals with their latest telemetry snapshot (For Dashboard Cards)
# --------------------------------------------------------------------------
@router.get("/", response_model=List[TerminalResponse])
def get_all_terminals(db: Session = Depends(get_db)):
    terminals = db.scalars(select(Terminal).order_by(Terminal.id)).all()
    results = []

    for term in terminals:
        # Fetch the most recent telemetry log for each terminal
        latest_log = db.scalars(
            select(TelemetryLog)
            .where(TelemetryLog.terminal_id == term.id)
            .order_by(desc(TelemetryLog.recorded_at))
            .limit(1)
        ).first()

        term_data = TerminalResponse(
            id=term.id,
            gate_name=term.gate_name,
            location_desc=term.location_desc,
            sim_phone_number=term.sim_phone_number,
            total_quota_mb=term.total_quota_mb,
            active_ussd_code=term.active_ussd_code,
            poll_interval_hours=term.poll_interval_hours,
            created_at=term.created_at,
            updated_at=term.updated_at,
            latest_balance_mb=latest_log.parsed_balance_mb if latest_log else None,
            latest_battery_level=latest_log.battery_level if latest_log else None,
            latest_battery_temp_c=latest_log.battery_temp_c if latest_log else None,
            latest_signal_dbm=latest_log.signal_strength_dbm if latest_log else None,
            last_seen=latest_log.recorded_at if latest_log else None
        )
        results.append(term_data)

    return results

# --------------------------------------------------------------------------
# 2. Register a new terminal (Add Terminal Modal)
# --------------------------------------------------------------------------
@router.post("/", response_model=TerminalResponse, status_code=status.HTTP_201_CREATED)
def create_terminal(terminal_in: TerminalCreate, db: Session = Depends(get_db)):
    existing = db.get(Terminal, terminal_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Terminal '{terminal_in.id}' is already registered."
        )

    terminal = Terminal(**terminal_in.model_dump())
    db.add(terminal)
    db.commit()
    db.refresh(terminal)
    return terminal

# --------------------------------------------------------------------------
# 3. Dynamic Configuration Check-in (Queried by Android Agent)
# --------------------------------------------------------------------------
@router.get("/{terminal_id}/config", response_model=TerminalConfigResponse)
def get_terminal_config(terminal_id: str, db: Session = Depends(get_db)):
    terminal = db.get(Terminal, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal '{terminal_id}' not found in registry."
        )

    return TerminalConfigResponse(
        terminal_id=terminal.id,
        active_ussd_code=terminal.active_ussd_code,
        poll_interval_hours=terminal.poll_interval_hours
    )

# --------------------------------------------------------------------------
# 4. Update Terminal Details & Dynamic USSD (Edit Modal)
# --------------------------------------------------------------------------
@router.put("/{terminal_id}", response_model=TerminalResponse)
def update_terminal(
    terminal_id: str, 
    terminal_in: TerminalUpdate, 
    db: Session = Depends(get_db)
):
    terminal = db.get(Terminal, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal '{terminal_id}' not found."
        )

    update_data = terminal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(terminal, field, value)

    terminal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(terminal)
    return terminal

# --------------------------------------------------------------------------
# 5. Delete a Terminal
# --------------------------------------------------------------------------
@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_terminal(terminal_id: str, db: Session = Depends(get_db)):
    terminal = db.get(Terminal, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal '{terminal_id}' not found."
        )

    db.delete(terminal)
    db.commit()
    return None

# --------------------------------------------------------------------------
# 6. Fetch Telemetry History (For Charts & Audits)
# --------------------------------------------------------------------------
@router.get("/{terminal_id}/history", response_model=List[TelemetryResponse])
def get_terminal_history(
    terminal_id: str, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    terminal = db.get(Terminal, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal '{terminal_id}' not found."
        )

    logs = db.scalars(
        select(TelemetryLog)
        .where(TelemetryLog.terminal_id == terminal_id)
        .order_by(desc(TelemetryLog.recorded_at))
        .limit(limit)
    ).all()

    return logs