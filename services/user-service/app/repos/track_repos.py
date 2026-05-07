from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.track import Track


class TrackRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: int, title: str, artist: str, tuning_name: str, string_names: List[str], frequencies: List[float]) -> Track:
        track = Track(
            title=title,
            artist=artist,
            tuning_name=tuning_name,
            string_names=string_names,
            frequencies=frequencies,
            owner_id=owner_id,
        )
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track

    def get_by_id(self, track_id: str) -> Track | None:
        return self.db.query(Track).options(joinedload(Track.owner)).filter(Track.id == track_id).first()

    def list_all(self, search: str | None = None) -> List[Track]:
        query = self.db.query(Track).options(joinedload(Track.owner))
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Track.title.ilike(pattern),
                    Track.artist.ilike(pattern),
                    Track.tuning_name.ilike(pattern),
                )
            )
        return query.order_by(Track.created_at.desc()).all()

    def list_by_user(self, owner_id: int, search: str | None = None) -> List[Track]:
        query = self.db.query(Track).options(joinedload(Track.owner)).filter(Track.owner_id == owner_id)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Track.title.ilike(pattern),
                    Track.artist.ilike(pattern),
                    Track.tuning_name.ilike(pattern),
                )
            )
        return query.order_by(Track.created_at.desc()).all()
