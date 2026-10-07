from pydantic import BaseModel

class MeasurementResponse(BaseModel):
    id: int
    geometry_type: str
    area_m2: float | None = None
    length_m: float | None = None