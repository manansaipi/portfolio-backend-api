import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.auth import get_current_admin
import cloudinary
import cloudinary.uploader

router = APIRouter(
    prefix="/api",
    tags=["upload"]
)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), current_user: str = Depends(get_current_admin)):
    if not os.getenv("CLOUDINARY_URL"):
        raise HTTPException(status_code=500, detail="Cloudinary is not configured on the server.")
        
    try:
        # Upload the file to Cloudinary using the file object
        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type="image",
            format="webp"
        )
        
        # Return the secure https URL provided by Cloudinary
        return {"url": result.get("secure_url")}
    except Exception as e:
        print(f"Error uploading to cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

from typing import List
from pydantic import BaseModel
import cloudinary.api

class DeleteLocalRequest(BaseModel):
    filename: str

class DeleteCloudinaryRequest(BaseModel):
    public_id: str

@router.get("/upload/local")
def get_local_photos(current_user: str = Depends(get_current_admin)):
    upload_dir = "static/img/uploads"
    if not os.path.exists(upload_dir):
        return []
    
    files = []
    for filename in os.listdir(upload_dir):
        filepath = os.path.join(upload_dir, filename)
        if os.path.isfile(filepath):
            # Return basic file info
            size = os.path.getsize(filepath)
            files.append({
                "filename": filename,
                "url": f"/{filepath}",
                "size": size
            })
    return files

@router.delete("/upload/local")
def delete_local_photo(payload: DeleteLocalRequest, current_user: str = Depends(get_current_admin)):
    upload_dir = "static/img/uploads"
    filepath = os.path.join(upload_dir, payload.filename)
    
    # Basic path traversal protection
    if not os.path.abspath(filepath).startswith(os.path.abspath(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    if os.path.exists(filepath) and os.path.isfile(filepath):
        os.remove(filepath)
        return {"message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/upload/cloudinary")
def get_cloudinary_photos(current_user: str = Depends(get_current_admin)):
    if not os.getenv("CLOUDINARY_URL"):
        raise HTTPException(status_code=500, detail="Cloudinary is not configured on the server.")
        
    try:
        # Fetch resources from cloudinary
        # max_results can be up to 500
        res = cloudinary.api.resources(type="upload", prefix="portfolio_uploads/", max_results=100)
        return res.get("resources", [])
    except Exception as e:
        print(f"Error fetching from cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Cloudinary photos")

@router.delete("/upload/cloudinary")
def delete_cloudinary_photo(payload: DeleteCloudinaryRequest, current_user: str = Depends(get_current_admin)):
    if not os.getenv("CLOUDINARY_URL"):
        raise HTTPException(status_code=500, detail="Cloudinary is not configured on the server.")
        
    try:
        res = cloudinary.uploader.destroy(payload.public_id)
        return {"message": "File deleted successfully", "result": res}
    except Exception as e:
        print(f"Error deleting from cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete Cloudinary photo")
