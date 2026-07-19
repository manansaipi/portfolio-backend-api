import os
from fastapi import APIRouter, UploadFile, File, Depends
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api",
    tags=["upload"]
)

# Ensure upload directory exists
os.makedirs("static/img/uploads", exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), current_user: str = Depends(get_current_admin)):
    file_location = f"static/img/uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    return {"url": f"/{file_location}"}
