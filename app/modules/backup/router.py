import os
import json
import urllib.request
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from app.core.database import get_db, engine

router = APIRouter(
    prefix="/api/backup",
    tags=["Backup & Export"]
)

def get_all_table_names():
    """Get all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def serialize_row(row):
    """Convert a SQLAlchemy row to a JSON-serializable dict."""
    result = {}
    for key, value in row._mapping.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, bytes):
            result[key] = value.decode('utf-8', errors='replace')
        else:
            result[key] = value
    return result

def send_backup_telegram_notification(success: bool, table_count: int = 0, total_rows: int = 0, error_msg: str = ""):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    
    bot_token = bot_token.strip(' "\'')
    chat_id = chat_id.strip(' "\'')

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if success:
        msg = (
            "🗄️ *Daily Database Backup Complete!*\n\n"
            f"✅ *Status:* Success\n"
            f"📅 *Date:* {now}\n"
            f"📊 *Tables:* {table_count} exported\n"
            f"📝 *Total Rows:* {total_rows}\n"
            "🔒 *Encrypted:* AES-256 & stored in GitHub Releases"
        )
    else:
        msg = (
            "❌ *Daily Database Backup FAILED!*\n\n"
            f"📅 *Date:* {now}\n"
            f"⚠️ *Error:* {error_msg}"
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

@router.get("/export")
def export_database(
    x_backup_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Export all database tables as JSON.
    Protected by a simple secret key passed via X-Backup-Key header.
    """
    backup_key = os.getenv("BACKUP_SECRET_KEY", "")
    if not backup_key or x_backup_key != backup_key:
        raise HTTPException(status_code=403, detail="Invalid or missing backup key")

    try:
        tables = get_all_table_names()
        backup_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "tables": {}
        }

        total_rows = 0
        for table_name in tables:
            try:
                rows = db.execute(text(f"SELECT * FROM `{table_name}`")).fetchall()
                serialized = [serialize_row(row) for row in rows]
                backup_data["tables"][table_name] = serialized
                total_rows += len(serialized)
            except Exception as e:
                backup_data["tables"][table_name] = {"error": str(e)}

        # Send success Telegram notification
        send_backup_telegram_notification(
            success=True,
            table_count=len(tables),
            total_rows=total_rows
        )

        return backup_data

    except Exception as e:
        # Send failure Telegram notification
        send_backup_telegram_notification(success=False, error_msg=str(e))
        raise HTTPException(status_code=500, detail=str(e))
