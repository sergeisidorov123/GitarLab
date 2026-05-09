from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user, get_current_user_optional
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(db)


@router.get("/track/{track_id}", response_model=List[CommentResponse])
async def get_comments_for_track(
    track_id: str,
    current_user: dict = Depends(get_current_user_optional),
    service: CommentService = Depends(get_comment_service),
):
    return service.get_comments_for_track(track_id)


@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    try:
        comment = service.create_comment(
            author_id=current_user["id"],
            author_username=current_user["username"],
            comment_data=comment_data
        )
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            author_username=comment.author_username,
            track_id=comment.track_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: dict = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    try:
        comment = service.update_comment(comment_id, current_user["id"], comment_data)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            author_username=comment.author_username,
            track_id=comment.track_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )
    except ValueError as exc:
        raise HTTPException(status_code=403 if "authorized" in str(exc) else 404, detail=str(exc))


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    try:
        success = service.delete_comment(comment_id, current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"detail": "Comment deleted successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=403 if "authorized" in str(exc) else 404, detail=str(exc))