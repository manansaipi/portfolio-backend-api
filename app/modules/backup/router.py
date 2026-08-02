import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import inspect

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

    tables = get_all_table_names()
    backup_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "tables": {}
    }

    for table_name in tables:
        try:
            from sqlalchemy import text
            rows = db.execute(text(f"SELECT * FROM `{table_name}`")).fetchall()
            backup_data["tables"][table_name] = [serialize_row(row) for row in rows]
        except Exception as e:
            backup_data["tables"][table_name] = {"error": str(e)}

    return backup_data
