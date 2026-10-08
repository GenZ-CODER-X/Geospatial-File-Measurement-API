from pydantic import BaseModel, ConfigDict
from typing import Any



class FeatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    geometry_type: str
    geometry: dict[str, Any]
    properties: dict[str, Any]