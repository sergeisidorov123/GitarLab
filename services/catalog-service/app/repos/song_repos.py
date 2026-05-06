from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.song import Song

class SongRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, song_id: str) -> Optional[Song]:
        result = await self.db.execute(
            select(Song).where(Song.id == song_id).options(selectinload(Song.tuning))
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Song]:
        result = await self.db.execute(select(Song).options(selectinload(Song.tuning)))
        return result.scalars().all()

    async def create(self, song_id: str, title: str, artist: str, tuning_id: int) -> Song:
        song = Song(id=song_id, title=title, artist=artist, tuning_id=tuning_id)
        self.db.add(song)
        await self.db.commit()
        await self.db.refresh(song)
        return song

    async def delete(self, song_id: str) -> bool:
        song = await self.get(song_id)
        if not song:
            return False
        await self.db.delete(song)
        await self.db.commit()
        return True