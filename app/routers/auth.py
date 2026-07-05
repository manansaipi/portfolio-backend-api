from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from .. import auth

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Check username
    if form_data.username != auth.ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check password
    if not auth.verify_password(form_data.password, auth.ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": auth.ADMIN_USERNAME}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
