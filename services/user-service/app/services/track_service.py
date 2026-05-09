from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repos.track_repos import TrackRepository
from app.repos.favorite_repos import FavoriteRepository
from app.models.user import User
from app.models.track import Track
from app.schemas.track import TrackCreate


class TrackService:
    def __init__(self, db: Session):
        self.track_repo = TrackRepository(db)
        self.favorite_repo = FavoriteRepository(db)
        self.db = db

    def create_track(self, user: User, payload: TrackCreate):
        existing = self.db.query(Track).filter(
            and_(
                Track.owner_id == user.id,
                Track.title == payload.title,
                Track.artist == payload.artist,
            )
        ).first()
        if existing:
            raise ValueError(f"Track '{payload.title}' by '{payload.artist}' already exists in your library")
        return self.track_repo.create(
            owner_id=user.id,
            title=payload.title,
            artist=payload.artist,
            tuning_name=payload.tuning_name,
            string_names=payload.string_names,
            frequencies=payload.frequencies,
        )

    def list_tracks(self, search: str | None = None):
        return self.track_repo.list_all(search)

    def list_my_tracks(self, user: User, search: str | None = None):
        return self.track_repo.list_by_user(user.id, search)

    def list_favorites(self, user: User):
        return self.favorite_repo.list_for_user(user.id)

    def favorite_track(self, user: User, track_id: str):
        track = self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError("Track not found")
        return self.favorite_repo.add(user.id, track_id)

    def unfavorite_track(self, user: User, track_id: str):
        track = self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError("Track not found")
        self.favorite_repo.remove(user.id, track_id)

    def is_favorite(self, user: User, track_id: str) -> bool:
        return self.favorite_repo.is_favorite(user.id, track_id)

    def edit_track(self, user: User, track_id: str, payload: TrackCreate):
        track = self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError("Track not found")
        if track.owner_id != user.id:
            raise ValueError("You do not own this track")
        track.title = payload.title
        track.artist = payload.artist
        track.tuning_name = payload.tuning_name
        track.string_names = payload.string_names
        track.frequencies = payload.frequencies
        self.track_repo.db.commit()
        self.track_repo.db.refresh(track)
        return track

    def delete_track(self, user: User, track_id: str):
        track = self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError("Track not found")
        if track.owner_id != user.id:
            raise ValueError("You do not own this track")
        self.track_repo.db.delete(track)
        self.track_repo.db.commit()
