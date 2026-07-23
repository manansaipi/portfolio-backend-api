from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import urllib.request
import json

from . import models, schemas
from app.core.database import get_db
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api/terminal/logs",
    tags=["Terminal Logs"]
)

import os

def send_telegram_notification(input_text: str, is_ai_mode: bool, response_text: str, ip_address: str, country: str = None, city: str = None, execution_time_ms: int = None):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    
    bot_token = bot_token.strip(' "\'')
    chat_id = chat_id.strip(' "\'')

    mode_str = "🤖 AI Mode" if is_ai_mode else "💻 System Command"
    loc_str = f"{city}, {country}" if (city and country) else (country or "Unknown Location")
    resp_snippet = (response_text[:200] + "...") if response_text and len(response_text) > 200 else (response_text or "-")
    exec_str = f"{execution_time_ms} ms" if execution_time_ms else "N/A"

    msg = (
        f"🖥️ *New Terminal Activity!*\n\n"
        f"📌 *Mode:* {mode_str}\n"
        f"💬 *Input:* `{input_text}`\n"
        f"🤖 *Response:* {resp_snippet}\n"
        f"📍 *Location:* {loc_str}\n"
        f"🌐 *IP:* `{ip_address}`\n"
        f"⏱️ *Latency:* {exec_str}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Telegram notification error: {e}")

def process_log_background(log_id: str, input_text: str, is_ai_mode: bool, response_text: str, execution_time_ms: int, ip_address: str, db: Session):
    country = None
    city = None
    if ip_address and ip_address not in ("127.0.0.1", "localhost", "::1"):
        try:
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip_address}?fields=country,city", timeout=5) as response:
                data = json.loads(response.read().decode())
                country = data.get("country")
                city = data.get("city")
                db_log = db.query(models.TerminalLog).filter(models.TerminalLog.id == log_id).first()
                if db_log:
                    db_log.country = country
                    db_log.city = city
                    db.commit()
        except Exception:
            pass

    # Send Telegram notification
    send_telegram_notification(
        input_text=input_text,
        is_ai_mode=is_ai_mode,
        response_text=response_text,
        ip_address=ip_address,
        country=country,
        city=city,
        execution_time_ms=execution_time_ms
    )

from app.core.rate_limiter import limiter

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
        referrer=log.referrer,
        audio_base64=log.audio_base64
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    background_tasks.add_task(
        process_log_background, 
        log_id=db_log.id, 
        input_text=log.input_text,
        is_ai_mode=log.is_ai_mode,
        response_text=log.response_text,
        execution_time_ms=log.execution_time_ms,
        ip_address=ip_address, 
        db=db
    )
    return db_log

@router.get("/countries", response_model=List[str])
def get_terminal_countries(db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)):
    countries = db.query(models.TerminalLog.country).filter(models.TerminalLog.country.isnot(None)).distinct().all()
    return sorted([c[0] for c in countries if c[0]])

@router.get("/ips", response_model=List[str])
def get_terminal_ips(db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)):
    ips = db.query(models.TerminalLog.ip_address).filter(models.TerminalLog.ip_address.isnot(None)).distinct().all()
    return sorted([ip[0] for ip in ips if ip[0]])

@router.get("/", response_model=schemas.TerminalLogPaginatedResponse)
def read_terminal_logs(
    skip: int = 0, 
    limit: int = 50, 
    search: str = None,
    is_ai_mode: str = None,
    country: str = None,
    ip_address: str = None,
    db: Session = Depends(get_db), 
    current_admin: str = Depends(get_current_admin)
):
    query = db.query(models.TerminalLog)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            models.TerminalLog.input_text.ilike(search_term) | 
            models.TerminalLog.response_text.ilike(search_term) |
            models.TerminalLog.ip_address.ilike(search_term)
        )
    
    if is_ai_mode is not None and is_ai_mode != "all":
        query = query.filter(models.TerminalLog.is_ai_mode == (is_ai_mode.lower() == "true" or is_ai_mode == "ai"))
        
    if country and country != "all":
        query = query.filter(models.TerminalLog.country == country)

    if ip_address and ip_address != "all":
        query = query.filter(models.TerminalLog.ip_address == ip_address)

    total = query.count()
    logs = query.order_by(models.TerminalLog.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": logs}

@router.delete("/")
def delete_terminal_logs(payload: schemas.DeleteLogsRequest, db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)):
    db.query(models.TerminalLog).filter(models.TerminalLog.id.in_(payload.log_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Successfully deleted {len(payload.log_ids)} logs"}
