from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth import get_current_admin, get_optional_current_admin
from ..rate_limiter import limiter

# Note: Some comment endpoints are nested under writings, e.g., /api/writings/{writing_id}/comments
# We will define them here but they can be included on the main app or the writings router.
# Let's define them here and we will include this router in main.py.

router = APIRouter(
    tags=["comments"]
)

@router.post("/api/writings/{writing_id}/comments", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_comment(request: Request, writing_id: str, comment: schemas.CommentCreate, db: Session = Depends(database.get_db), current_user: str | None = Depends(get_optional_current_admin)):
    # Verify writing exists
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
        
    # If parent_id is provided, verify it exists and belongs to the same writing
    if comment.parent_id:
        db_parent = db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
        if not db_parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if db_parent.writing_id != writing_id:
            raise HTTPException(status_code=400, detail="Parent comment belongs to a different writing")
            
    is_author = current_user is not None
    db_comment = models.Comment(**comment.model_dump(), writing_id=writing_id, is_author=is_author)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/api/writings/{writing_id}/comments", response_model=List[schemas.Comment])
def get_comments(writing_id: str, db: Session = Depends(database.get_db)):
    # Verify writing exists
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
        
    # Fetch all comments for the writing
    comments_flat = db.query(models.Comment).filter(models.Comment.writing_id == writing_id).order_by(models.Comment.created_at.asc()).all()
    
    # Build tree
    comment_dict = {}
    for c in comments_flat:
        c_dict = {
            "id": c.id,
            "writing_id": c.writing_id,
            "parent_id": c.parent_id,
            "username": c.username,
            "content": c.content,
            "created_at": c.created_at,
            "profile_img": c.profile_img,
            "likes": c.likes,
            "is_author": c.is_author,
            "replies": []
        }
        comment_dict[c.id] = schemas.Comment(**c_dict)
        
    tree = []
    for c in comments_flat:
        if c.parent_id:
            parent = comment_dict.get(c.parent_id)
            if parent:
                parent.replies.append(comment_dict[c.id])
        else:
            tree.append(comment_dict[c.id])
            
    return tree

@router.put("/api/comments/{comment_id}/like", response_model=schemas.Comment)
def like_comment(comment_id: str, db: Session = Depends(database.get_db)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    db_comment.likes += 1
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.put("/api/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: str, comment_update: schemas.CommentUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    update_data = comment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_comment, key, value)
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    db.delete(db_comment)
    db.commit()
    return None
