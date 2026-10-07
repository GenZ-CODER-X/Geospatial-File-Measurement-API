from sqlalchemy.orm import Session

from app.models.uploaded_file import UploadedFile


def create_file(
    db: Session,
    file: UploadedFile,
) -> UploadedFile:
    db.add(file)
    db.flush()

    return file


def get_file_by_id(
    db: Session,
    file_id,
) -> UploadedFile | None:
    return (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id)
        .first()
    )