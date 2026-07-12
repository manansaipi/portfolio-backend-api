from pydantic import BaseModel
from typing import Optional

class FavoriteBase(BaseModel):
    movie_id: int
    title: str
    poster_path: Optional[str] = None

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteOut(FavoriteBase):
    id: int
    user_id: str

    class Config:
        from_attributes = True
