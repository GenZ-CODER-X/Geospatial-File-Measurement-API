from sqlalchemy import Column, Integer, String, TIMESTAMP, text, UUID, JSON

from app.db.database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID, primary_key=True)
    filename = Column(String, nullable=False)

    feature_count = Column(Integer, nullable=False)
    columns = Column(JSON)
    geometry_types = Column(JSON)

    crs = Column(String)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
    )