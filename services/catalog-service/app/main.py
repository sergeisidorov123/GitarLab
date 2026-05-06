from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.api import health, songs
from app.repos.song_repos import SongRepository
from app.repos.tuning_repos import TuningRepository

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed_data():
    async with AsyncSessionLocal() as session:
        tuning_repo = TuningRepository(session)
        song_repo = SongRepository(session)

        standard_tuning = await tuning_repo.get_by_name("Standard")
        if not standard_tuning:
            standard_tuning = await tuning_repo.create(
                name="Standard",
                string_names=["E", "A", "D", "G", "B", "E"],
                frequencies=[82.41, 110.00, 146.83, 196.00, 246.94, 329.63],
            )

        songs = await song_repo.get_all()
        if not songs:
            await song_repo.create(
                song_id="song1",
                title="Stairway to Heaven",
                artist="Led Zeppelin",
                tuning_id=standard_tuning.id,
            )
            await song_repo.create(
                song_id="song2",
                title="Wonderwall",
                artist="Oasis",
                tuning_id=standard_tuning.id,
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

@app.on_event("startup")
async def on_startup():
    await init_db()
    await seed_data()