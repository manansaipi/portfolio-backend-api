import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set!")
    exit(1)

engine = create_engine(DATABASE_URL)

columns = [
    ("category", "VARCHAR(50)"),
    ("title", "VARCHAR(255)"),
    ("description", "TEXT"),
    ("location", "VARCHAR(255)"),
    ("date_taken", "VARCHAR(50)"),
    ("camera", "VARCHAR(100)"),
    ("lens", "VARCHAR(100)"),
    ("tags", "VARCHAR(500)"),
    ("is_featured", "BOOLEAN DEFAULT FALSE")
]

with engine.connect() as conn:
    for col_name, col_type in columns:
        try:
            sql = text(f"ALTER TABLE gallery_media ADD COLUMN {col_name} {col_type};")
            conn.execute(sql)
            conn.commit()
            print(f"Added column {col_name}")
        except Exception as e:
            print(f"Column {col_name} might already exist or error: {e}")

print("Database schema migration completed successfully!")
