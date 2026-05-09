from pydantic import BaseModel
from typing import List


class TuningResponse(BaseModel):
    id: int
    name: str
    string_names: List[str]
    frequencies: List[float]

    class Config:
        from_attributes = True
