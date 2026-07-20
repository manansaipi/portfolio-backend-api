import os
import sys
from dotenv import load_dotenv

# Ensure the backend directory is in the path
sys.path.append("/home/manansaipi/projects/portfolio-website/backend")
load_dotenv("/home/manansaipi/projects/portfolio-website/backend/.env")

from app.core.database import engine
from sqlalchemy import text

def migrate():
    print("Starting migration...")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE terminal_logs ADD COLUMN audio_base64 MEDIUMTEXT NULL;"))
            print("Successfully added audio_base64 column.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Column already exists. Skipping.")
            else:
                print(f"Error during migration: {e}")
                raise e

if __name__ == "__main__":
    migrate()
