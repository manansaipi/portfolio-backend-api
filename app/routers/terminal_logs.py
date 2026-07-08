from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import urllib.request
import json

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_admin

router = APIRouter(
    prefix="/api/terminal/logs",
    tags=["Terminal Logs"]
)

def fetch_location(log_id: str, ip_address: str, db: Session):
    if not ip_address or ip_address in ("127.0.0.1", "localhost", "::1"):
        return
    try:
        with urllib.request.urlopen(f"http://ip-api.com/json/{ip_address}?fields=country,city", timeout=5) as response:
            data = json.loads(response.read().decode())
            db_log = db.query(models.TerminalLog).filter(models.TerminalLog.id == log_id).first()
            if db_log:
                db_log.country = data.get("country")
                db_log.city = data.get("city")
                db.commit()
    except Exception:
        pass

from ..rate_limiter import limiter

@router.post("/", response_model=schemas.TerminalLogResponse)
@limiter.limit("30/minute")
def create_terminal_log(log: schemas.TerminalLogCreate, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Try to get the real IP if behind a proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    user_agent = request.headers.get("User-Agent")

    db_log = models.TerminalLog(
        input_text=log.input_text,
        is_ai_mode=log.is_ai_mode,
        response_text=log.response_text,
        execution_time_ms=log.execution_time_ms,
        ip_address=ip_address,
        user_agent=user_agent,
        screen_width=log.screen_width,
        screen_height=log.screen_height,
        language=log.language,
        referrer=log.referrer
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    background_tasks.add_task(fetch_location, db_log.id, ip_address, db)
    return db_log

@router.get("/", response_model=schemas.TerminalLogPaginatedResponse)
def read_terminal_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)):
    total = db.query(models.TerminalLog).count()
    logs = db.query(models.TerminalLog).order_by(models.TerminalLog.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": logs}

@router.delete("/")
def delete_terminal_logs(payload: schemas.DeleteLogsRequest, db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)):
    db.query(models.TerminalLog).filter(models.TerminalLog.id.in_(payload.log_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Successfully deleted {len(payload.log_ids)} logs"}
