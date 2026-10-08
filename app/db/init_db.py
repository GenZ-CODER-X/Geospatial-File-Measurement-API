from app.db.database import Base, engine

from app.models.uploaded_file import UploadedFile
from app.models.feature import Feature
from app.models.measurement import Measurement


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully")