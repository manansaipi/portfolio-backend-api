import os
import sys

# Add the backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.modules.users.models import User
from dotenv import load_dotenv

load_dotenv()

# Initialize tables if not already created
Base.metadata.create_all(bind=engine)

def create_initial_admin():
    db = SessionLocal()
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
    
    if not admin_password_hash:
        print("Warning: ADMIN_PASSWORD_HASH is empty in .env. Admin user might not be able to log in.")

    # Check if admin already exists
    admin_user = db.query(User).filter(User.user_name == admin_username).first()
    if not admin_user:
        print(f"Creating initial admin user: {admin_username}")
        # The password in .env is already hashed, so we insert it directly
        db_user = User(
            user_name=admin_username,
            hashed_password=admin_password_hash,
            is_admin=True
        )
        db.add(db_user)
        db.commit()
        print("Admin user created successfully!")
    else:
        # Make sure they are admin
        if not admin_user.is_admin:
            admin_user.is_admin = True
            db.commit()
            print(f"User {admin_username} updated to admin.")
        else:
            print(f"Admin user {admin_username} already exists.")
            
    db.close()

if __name__ == "__main__":
    create_initial_admin()
