from pydantic import BaseModel
from typing import Optional

class TuningResult(BaseModel):
    """Результат настройки"""
    frequency: float
    note: Optional[str] = None
    cents: int = 0
    is_in_tune: bool = False
    suggestion: str = ""

class HealthResponse(BaseModel):
    status: str
    service: str