from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tuning import Tuning

class TuningRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Optional[Tuning]:
        result = await self.db.execute(select(Tuning).where(Tuning.name == name))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Tuning]:
        result = await self.db.execute(select(Tuning))
        return result.scalars().all()

    async def create(self, name: str, string_names: list, frequencies: list) -> Tuning:
        tuning = Tuning(name=name, string_names=string_names, frequencies=frequencies)
        self.db.add(tuning)
        await self.db.commit()
        await self.db.refresh(tuning)
        return tuning