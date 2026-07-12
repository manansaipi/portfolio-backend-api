from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas import favorite as favoriteSchema
from app.models.favorite import Favorite
from app.models.user import User
from app.core.database import get_db
from app.core import auth

router = APIRouter(
    prefix="/api/favorites",
    tags=["favorites"]
)

@router.get("", response_model=List[favoriteSchema.FavoriteOut])
def list_favorites(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Using user_name as user_id for Netflix backend compatibility
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.user_name).all()
    return favorites

@router.post("/add-favorite", response_model=favoriteSchema.FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(favorite_data: favoriteSchema.FavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.user_name,
        Favorite.movie_id == favorite_data.movie_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie already in favorites",
        )

    db_favorite = Favorite(
        user_id=current_user.user_name,  # Force user_id to match current_user for security
        movie_id=favorite_data.movie_id,
        title=favorite_data.title,
        poster_path=favorite_data.poster_path
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@router.delete("/{fav_id}", status_code=status.HTTP_200_OK)
def remove_favorite(fav_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    favorite = db.query(Favorite).filter(
        Favorite.id == fav_id, 
        Favorite.user_id == current_user.user_name
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found or not authorized",
        )
        
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed"}
