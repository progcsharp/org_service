from pydantic import BaseModel


class ActivityCreate(BaseModel):
    name: str
    parent_id: int | None = None


class ActivityUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None