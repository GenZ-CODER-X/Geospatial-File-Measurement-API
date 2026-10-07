from sqlalchemy import Column, Integer, Float, ForeignKey, String

from app.db.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)

    file_id = Column(
        ForeignKey("uploaded_files.id"),
        nullable=False,
    )

    feature_id = Column(
        ForeignKey("features.id"),
        nullable=False,
    )

    geometry_type = Column(String, nullable=False)

    area_m2 = Column(Float, nullable=True)
    length_m = Column(Float, nullable=True)