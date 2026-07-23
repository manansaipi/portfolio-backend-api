import os
import json
import urllib.request
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(
    prefix="/api/keep-alive",
    tags=["Health & System"]
)

def send_keep_alive_telegram_notification():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    
    bot_token = bot_token.strip(' "\'')
    chat_id = chat_id.strip(' "\'')

    msg = (
        "⏰ *Scheduled Database Keep-Alive Triggered!*\n\n"
        "🟢 *Server Status:* Active & Responded\n"
        "🗄️ *Database:* Pinged (`SELECT 1`) successfully!"
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

@router.get("")
def keep_alive(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        
        # Send Telegram notification
        send_keep_alive_telegram_notification()
        
        return {"status": "ok", "database": "connected", "message": "Backend and Database kept alive successfully!"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
