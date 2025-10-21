from pydantic import BaseModel

class BuildingCreate(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingUpdate(BaseModel):
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None