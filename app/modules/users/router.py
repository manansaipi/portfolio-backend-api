from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from . import schemas as userSchema
from .models import User
from app.core.database import get_db
from app.core import auth

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.post("/register", response_model=userSchema.UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: userSchema.UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User name already registered",
        )
    
    hashed_password = auth.get_password_hash(user.password)

    db_user = User(
        user_name=user.user_name, 
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
def login_for_access_token(user: userSchema.UserAuth, db: Session = Depends(get_db)):
    user_in_db = db.query(User).filter(User.user_name == user.user_name).first()

    if not user_in_db or not auth.verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user name or password",
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# --- ADMIN ENDPOINTS ---

from typing import List

@router.get("", response_model=List[userSchema.UserInDB])
def list_users(db: Session = Depends(get_db), current_admin: User = Depends(auth.get_current_admin)):
    users = db.query(User).all()
    return users

@router.post("", response_model=userSchema.UserInDB, status_code=status.HTTP_201_CREATED)
def create_user_admin(user: userSchema.UserCreateAdmin, db: Session = Depends(get_db), current_admin: User = Depends(auth.get_current_admin)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User name already registered",
        )
    
    hashed_password = auth.get_password_hash(user.password)

    db_user = User(
        user_name=user.user_name, 
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(auth.get_current_admin)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if db_user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
        
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
