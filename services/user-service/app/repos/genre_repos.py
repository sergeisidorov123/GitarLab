from typing import List
from sqlalchemy.orm import Session
from app.models.genre import Genre


class GenreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, name: str) -> Genre:
        """Get genre by name or create if doesn't exist."""
        genre = self.db.query(Genre).filter(Genre.name.ilike(name)).first()
        if genre:
            return genre
        
        # Create new genre
        genre = Genre(name=name)
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return genre

    def get_by_id(self, genre_id: int) -> Genre | None:
        return self.db.query(Genre).filter(Genre.id == genre_id).first()

    def get_by_name(self, name: str) -> Genre | None:
        return self.db.query(Genre).filter(Genre.name.ilike(name)).first()

    def get_all(self) -> List[Genre]:
        return self.db.query(Genre).order_by(Genre.name).all()

    def create(self, name: str) -> Genre:
        """Create a new genre, but don't fail if it already exists."""
        existing = self.get_by_name(name)
        if existing:
            return existing
        
        genre = Genre(name=name)
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return genre
