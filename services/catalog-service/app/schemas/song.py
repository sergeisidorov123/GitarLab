from pydantic import BaseModel
from typing import List, Optional

class TuningResponse(BaseModel):
    name: str
    string_names: List[str]
    frequencies: List[float]

class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    tuning: TuningResponse

class SongListResponse(BaseModel):
    id: str
    title: str
    artist: str

class SongCreate(BaseModel):
    id: str
    title: str
    artist: str
    tuning_name: str