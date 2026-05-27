from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user, get_current_user_optional
from app.schemas.track import TrackCreate, TrackResponse, GenreResponse
from app.models.user import User
from app.services.track_service import TrackService

router = APIRouter(prefix="/tracks", tags=["tracks"])


def get_track_service(db: Session = Depends(get_db)) -> TrackService:
    return TrackService(db)


def build_track_response(track, service: TrackService, current_user: User = None) -> TrackResponse:
    """Helper function to build TrackResponse with genres."""
    genres = [GenreResponse(id=g.genre.id, name=g.genre.name) for g in track.genres]
    return TrackResponse(
        id=track.id,
        title=track.title,
        artist=track.artist,
        tuning_name=track.tuning_name,
        string_names=track.string_names,
        frequencies=track.frequencies,
        owner_id=track.owner_id,
        owner_username=track.owner.username if track.owner else "",
        created_at=track.created_at,
        is_favorite=service.is_favorite(current_user, track.id) if current_user else False,
        genres=genres,
    )


@router.get("/", response_model=List[TrackResponse])
def list_tracks(
    search: str | None = None,
    current_user: User = Depends(get_current_user_optional),
    service: TrackService = Depends(get_track_service),
):
    return [
        build_track_response(track, service, current_user)
        for track in service.list_tracks(search)
    ]


@router.get("/my", response_model=List[TrackResponse])
def list_my_tracks(
    current_user: User = Depends(get_current_user),
    search: str | None = None,
    service: TrackService = Depends(get_track_service),
):
    return [
        build_track_response(track, service, current_user)
        for track in service.list_my_tracks(current_user, search)
    ]


@router.get("/favorites", response_model=List[TrackResponse])
def list_favorites(current_user: User = Depends(get_current_user), service: TrackService = Depends(get_track_service)):
    return [
        build_track_response(track, service, current_user)
        for track in service.list_favorites(current_user)
    ]


@router.get("/{track_id}", response_model=TrackResponse)
def get_track(
    track_id: str,
    current_user: User = Depends(get_current_user_optional),
    service: TrackService = Depends(get_track_service),
):
    try:
        track = service.get_track(track_id)
        return build_track_response(track, service, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=TrackResponse)
def create_track(
    payload: TrackCreate,
    current_user: User = Depends(get_current_user),
    service: TrackService = Depends(get_track_service),
):
    try:
        track = service.create_track(current_user, payload)
        return build_track_response(track, service, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{track_id}/favorite")
def favorite_track(track_id: str, current_user: User = Depends(get_current_user), service: TrackService = Depends(get_track_service)):
    try:
        service.favorite_track(current_user, track_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"detail": "Track added to favorites"}


@router.delete("/{track_id}/favorite")
def unfavorite_track(track_id: str, current_user: User = Depends(get_current_user), service: TrackService = Depends(get_track_service)):
    try:
        service.unfavorite_track(current_user, track_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"detail": "Track removed from favorites"}


@router.put("/{track_id}", response_model=TrackResponse)
def edit_track(
    track_id: str,
    payload: TrackCreate,
    current_user: User = Depends(get_current_user),
    service: TrackService = Depends(get_track_service),
):
    try:
        track = service.edit_track(current_user, track_id, payload)
        return build_track_response(track, service, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=403 if "not own" in str(exc) else 404, detail=str(exc))


@router.delete("/{track_id}")
def delete_track(track_id: str, current_user: User = Depends(get_current_user), service: TrackService = Depends(get_track_service)):
    try:
        service.delete_track(current_user, track_id)
    except ValueError as exc:
        raise HTTPException(status_code=403 if "not own" in str(exc) else 404, detail=str(exc))
    return {"detail": "Track deleted successfully"}
