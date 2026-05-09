from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import auth, tracks, health
from app.services.auth_service import AuthService

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tracks.router)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        auth_service.ensure_roles_exist()
        if not auth_service.has_admin_user():
            auth_service.create_admin_user("admin", "admin123")
    finally:
        db.close()
