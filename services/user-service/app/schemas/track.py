from datetime import datetime
from typing import List
from pydantic import BaseModel


class TrackCreate(BaseModel):
    title: str
    artist: str
    tuning_name: str
    string_names: List[str]
    frequencies: List[float]


class TrackResponse(TrackCreate):
    id: str
    owner_id: int
    owner_username: str
    created_at: datetime

    class Config:
        orm_mode = True
