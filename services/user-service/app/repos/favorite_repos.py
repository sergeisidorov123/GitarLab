from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models.favorite import Favorite
from app.models.track import Track


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, user_id: int, track_id: str) -> Favorite | None:
        existing = self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id,
        ).first()
        if existing:
            return existing
        favorite = Favorite(user_id=user_id, track_id=track_id)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def remove(self, user_id: int, track_id: str) -> None:
        favorite = self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id,
        ).first()
        if favorite:
            self.db.delete(favorite)
            self.db.commit()

    def list_for_user(self, user_id: int) -> List[Track]:
        return (
            self.db.query(Track)
            .join(Favorite, Favorite.track_id == Track.id)
            .options(joinedload(Track.owner))
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def is_favorite(self, user_id: int, track_id: str) -> bool:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.track_id == track_id)
            .first()
            is not None
        )
