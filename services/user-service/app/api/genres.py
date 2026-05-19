from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repos.genre_repos import GenreRepository
from app.schemas.track import GenreResponse

router = APIRouter(prefix="/genres", tags=["genres"])


def get_genre_repo(db: Session = Depends(get_db)) -> GenreRepository:
    return GenreRepository(db)


@router.get("/", response_model=List[GenreResponse])
def list_genres(repo: GenreRepository = Depends(get_genre_repo)):
    """Get all available genres."""
    return repo.get_all()


@router.post("/", response_model=GenreResponse)
def create_genre(name: str, repo: GenreRepository = Depends(get_genre_repo)):
    """Create a new genre or return existing if already exists."""
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Genre name cannot be empty")
    
    genre = repo.get_or_create(name.strip())
    return GenreResponse(id=genre.id, name=genre.name)
