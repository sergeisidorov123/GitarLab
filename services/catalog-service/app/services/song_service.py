from typing import List, Optional
from app.repos.song_repos import SongRepository
from app.repos.tuning_repos import TuningRepository
from app.schemas.song import SongResponse, TuningResponse, SongCreate

class SongService:
    def __init__(self, song_repo: SongRepository):
        self.song_repo = song_repo

    async def get_song(self, song_id: str) -> Optional[SongResponse]:
        song = await self.song_repo.get(song_id)
        if not song:
            return None
        return SongResponse(
            id=song.id,
            title=song.title,
            artist=song.artist,
            tuning=TuningResponse(
                name=song.tuning.name,
                string_names=song.tuning.string_names,
                frequencies=song.tuning.frequencies
            )
        )

    async def list_songs(self) -> List[dict]:
        songs = await self.song_repo.get_all()
        return [{"id": s.id, "title": s.title, "artist": s.artist} for s in songs]

    async def create_song(self, song_data: SongCreate) -> SongResponse:
        # First get or create the tuning
        tuning_repo = TuningRepository(self.song_repo.db)
        tuning = await tuning_repo.get_by_name(song_data.tuning_name)
        if not tuning:
            # Create standard guitar tuning if it doesn't exist
            if song_data.tuning_name == "Standard":
                tuning = await tuning_repo.create(
                    name="Standard",
                    string_names=["E", "A", "D", "G", "B", "E"],
                    frequencies=[82.41, 110.00, 146.83, 196.00, 246.94, 329.63]
                )
            else:
                raise ValueError(f"Tuning '{song_data.tuning_name}' not found")

        song = await self.song_repo.create(song_data.id, song_data.title, song_data.artist, tuning.id)
        return SongResponse(
            id=song.id,
            title=song.title,
            artist=song.artist,
            tuning=TuningResponse(
                name=tuning.name,
                string_names=tuning.string_names,
                frequencies=tuning.frequencies
            )
        )