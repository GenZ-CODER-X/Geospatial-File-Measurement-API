from pydantic import BaseModel,ConfigDict

class MeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    geometry_type: str
    area_m2: float | None = None
    length_m: float | None = None