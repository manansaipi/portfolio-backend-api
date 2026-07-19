from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    movie_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    poster_path = Column(String(255))
