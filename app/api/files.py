from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.file import FileResponse
from app.services.file_service import process_uploaded_file, get_file_details


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".zip", ".kml")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .zip and .kml files are supported",
        )
    file_id = uuid4()
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    try:
        uploaded_file = process_uploaded_file(
            db=db,
            file_id=file_id,
            file_path=file_path,
            filename=file.filename,
        )

        return uploaded_file

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    
@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id,
    db: Session = Depends(get_db),
):
    try:
        return get_file_details(
            db=db,
            file_id=file_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )