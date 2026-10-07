from pydantic import BaseModel
from typing import Any


class Feature(BaseModel):
    id: int
    geometry_type: str
    geometry: dict[str, Any]
    properties: dict[str, Any]


class Measurement(BaseModel):
    id: int
    geometry_type: str
    area_m2: float | None = None
    length_m: float | None = None


class FileRecord(BaseModel):
    id: str
    filename: str
    feature_count: int
    columns: list[str]
    geometry_types: list[str]
    crs: str
    features: list[Feature]
    measurements: list[Measurement]