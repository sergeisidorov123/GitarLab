from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repos.song_repos import SongRepository
from app.services.song_service import SongService
from app.schemas.song import SongResponse, SongCreate

router = APIRouter(prefix="/songs", tags=["songs"])

def get_song_service(db: AsyncSession = Depends(get_db)) -> SongService:
    repo = SongRepository(db)
    return SongService(repo)

@router.get("/")
async def list_songs(service: SongService = Depends(get_song_service)):
    return await service.list_songs()

@router.post("/", response_model=SongResponse)
async def create_song(song: SongCreate, service: SongService = Depends(get_song_service)):
    try:
        return await service.create_song(song)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{song_id}", response_model=SongResponse)
async def get_song(song_id: str, service: SongService = Depends(get_song_service)):
    song = await service.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.get("/{song_id}/tuning")
async def get_tuning(song_id: str, service: SongService = Depends(get_song_service)):
    song = await service.get_song(song_id)
    if not song:
        raise HTTPException(404, "Song not found")
    return song.tuning