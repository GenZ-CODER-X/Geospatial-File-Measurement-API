from sqlalchemy import Column, Integer, ForeignKey, JSON, String

from app.db.database import Base


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True)
    file_id = Column(
        ForeignKey("uploaded_files.id"),
        nullable=False,
    )

    feature_index = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)
    geometry = Column(JSON, nullable=False)
    properties = Column(JSON)