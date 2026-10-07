from pydantic import BaseModel
from typing import Any


class FeatureResponse(BaseModel):
    id: int
    geometry_type: str
    geometry: dict[str, Any]
    properties: dict[str, Any]