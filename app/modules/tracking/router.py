import os
import json
import urllib.request
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)

class PageVisitPayload(BaseModel):
    pathname: str
    userAgent: str

def send_visit_telegram_notification(pathname: str, user_agent: str, ip_address: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    
    bot_token = bot_token.strip(' "\'')
    chat_id = chat_id.strip(' "\'')

    msg = (
        "👀 *New Visitor Navigation!*\n\n"
        f"📍 *Path:* `{pathname}`\n"
        f"🌐 *IP:* `{ip_address}`\n"
        f"📱 *Device:* `{user_agent}`\n"
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

@router.post("")
async def track_page_visit(payload: PageVisitPayload, request: Request):
    try:
        # Get client IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.client.host if request.client else "Unknown"

        # Send Telegram notification
        send_visit_telegram_notification(
            pathname=payload.pathname,
            user_agent=payload.userAgent,
            ip_address=ip_address
        )
        
        return {"status": "ok", "message": "Visit tracked"}
    except Exception as e:
        print(f"Tracking error: {e}")
        return {"status": "error", "message": str(e)}
