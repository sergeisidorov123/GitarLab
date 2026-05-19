from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TrackCreate(BaseModel):
    title: str
    artist: str
    tuning_name: str
    string_names: List[str]
    frequencies: List[float]
    genre_names: Optional[List[str]] = None  # User can provide genre names


class TrackResponse(TrackCreate):
    id: str
    owner_id: int
    owner_username: str
    created_at: datetime
    is_favorite: Optional[bool] = False
    genres: Optional[List[GenreResponse]] = []

    class Config:
        orm_mode = True
