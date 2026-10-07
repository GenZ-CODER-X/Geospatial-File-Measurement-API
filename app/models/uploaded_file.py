from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text,UUID
from db.database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID, primary_key=True)
    filename = Column(String, nullable=False)
    crs = Column(String)
    feature_count = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'))