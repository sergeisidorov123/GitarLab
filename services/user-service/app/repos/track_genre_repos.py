from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models.track_genre import TrackGenre
from app.models.genre import Genre


class TrackGenreRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_genre(self, track_id: str, genre_id: int) -> TrackGenre | None:
        """Add a genre to a track."""
        existing = self.db.query(TrackGenre).filter(
            TrackGenre.track_id == track_id,
            TrackGenre.genre_id == genre_id,
        ).first()
        if existing:
            return existing
        
        track_genre = TrackGenre(track_id=track_id, genre_id=genre_id)
        self.db.add(track_genre)
        self.db.commit()
        self.db.refresh(track_genre)
        return track_genre

    def remove_genre(self, track_id: str, genre_id: int) -> None:
        """Remove a genre from a track."""
        track_genre = self.db.query(TrackGenre).filter(
            TrackGenre.track_id == track_id,
            TrackGenre.genre_id == genre_id,
        ).first()
        if track_genre:
            self.db.delete(track_genre)
            self.db.commit()

    def get_track_genres(self, track_id: str) -> List[Genre]:
        """Get all genres for a track."""
        return (
            self.db.query(Genre)
            .join(TrackGenre, TrackGenre.genre_id == Genre.id)
            .filter(TrackGenre.track_id == track_id)
            .order_by(Genre.name)
            .all()
        )

    def clear_track_genres(self, track_id: str) -> None:
        """Remove all genres from a track."""
        self.db.query(TrackGenre).filter(TrackGenre.track_id == track_id).delete()
        self.db.commit()

    def set_track_genres(self, track_id: str, genre_ids: List[int]) -> None:
        """Set genres for a track, replacing existing ones."""
        self.clear_track_genres(track_id)
        for genre_id in genre_ids:
            self.add_genre(track_id, genre_id)
