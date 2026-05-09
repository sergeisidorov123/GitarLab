from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.tuning import TuningResponse
from app.repos.tuning_repos import TuningRepository

router = APIRouter(prefix="/tunings", tags=["tunings"])


def get_tuning_repo(db: AsyncSession = Depends(get_db)) -> TuningRepository:
    return TuningRepository(db)


@router.get("/", response_model=List[TuningResponse])
async def list_tunings(repo: TuningRepository = Depends(get_tuning_repo)):
    """Get all available tunings"""
    tunings = await repo.get_all()
    return tunings
