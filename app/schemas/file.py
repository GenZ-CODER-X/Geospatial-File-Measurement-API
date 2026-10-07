from pydantic import BaseModel

from feature import FeatureResponse
from .measurement import MeasurementResponse


class FileResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    columns: list[str]
    geometry_types: list[str]
    crs: str
    features: list[FeatureResponse]
    measurements: list[MeasurementResponse]


class MeasurementsResponse(BaseModel):
    file_id: str
    measurements: list[MeasurementResponse]