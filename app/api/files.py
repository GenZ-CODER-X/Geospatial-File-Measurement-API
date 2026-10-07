from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.file import FileResponse, MeasurementsResponse


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


@router.post("/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    pass


@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    pass


@router.get(
    "/{file_id}/measurements/",
    response_model=MeasurementsResponse,
)
def get_measurements(
    file_id: str,
    db: Session = Depends(get_db),
):
    pass