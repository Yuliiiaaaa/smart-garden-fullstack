from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.storage import StorageService
from app.api.dependencies import get_current_user


router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    storage: StorageService = Depends(),
    current_user = Depends(get_current_user)
):
    key = await storage.upload_file(file, folder=f"users/{current_user.id}")
    return {"key": key}

@router.get("/presigned/{key:path}")
async def get_presigned_url(
    key: str,
    storage: StorageService = Depends(),
    current_user = Depends(get_current_user)
):
    url = storage.get_presigned_url(key)
    if not url:
        raise HTTPException(404, "File not found")
    return {"url": url}