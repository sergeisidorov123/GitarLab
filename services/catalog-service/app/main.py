from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.api import health, songs, tunings
from app.repos.song_repos import SongRepository
from app.repos.tuning_repos import TuningRepository

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed_data():
    async with AsyncSessionLocal() as session:
        tuning_repo = TuningRepository(session)
        song_repo = SongRepository(session)

        # Define all preset tunings
        presets = [
            ("Standard", ["E", "A", "D", "G", "B", "E"], [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]),
            ("Drop D", ["D", "A", "D", "G", "B", "E"], [73.42, 110.00, 146.83, 196.00, 246.94, 329.63]),
            ("Half Step Down", ["D#", "G#", "C#", "F#", "A#", "D#"], [77.78, 103.83, 138.59, 185.00, 233.08, 311.13]),
            ("Full Step Down", ["D", "G", "C", "F", "A", "D"], [73.42, 98.00, 130.81, 174.61, 220.00, 293.66]),
            ("Open G", ["D", "G", "D", "G", "B", "D"], [73.42, 98.00, 146.83, 196.00, 246.94, 293.66]),
            ("Open E", ["E", "B", "E", "G#", "B", "E"], [82.41, 123.47, 164.81, 207.65, 246.94, 329.63]),
            ("Open D", ["D", "A", "D", "F#", "A", "D"], [73.42, 110.00, 146.83, 185.00, 220.00, 293.66]),
        ]

        # Create tunings if they don't exist
        tuning_map = {}
        for name, strings, freqs in presets:
            existing = await tuning_repo.get_by_name(name)
            if existing:
                tuning_map[name] = existing
            else:
                tuning = await tuning_repo.create(name=name, string_names=strings, frequencies=freqs)
                tuning_map[name] = tuning

        # Create sample songs
        songs = await song_repo.get_all()
        if not songs:
            await song_repo.create(
                song_id="song1",
                title="Stairway to Heaven",
                artist="Led Zeppelin",
                tuning_id=tuning_map["Standard"].id,
            )
            await song_repo.create(
                song_id="song2",
                title="Wonderwall",
                artist="Oasis",
                tuning_id=tuning_map["Standard"].id,
            )

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(songs.router)
app.include_router(tunings.router)

@app.on_event("startup")
async def on_startup():
    await init_db()
    await seed_data()