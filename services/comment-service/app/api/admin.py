from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.comment import CommentAdminResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/admin/comments", tags=["admin-comments"])


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(db)


@router.get("/", response_model=List[CommentAdminResponse])
async def get_all_comments(
    current_user: dict = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    comments = service.get_all_comments_for_admin()
    return [
        CommentAdminResponse(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            author_username=comment.author_username,
            track_id=comment.track_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_deleted=comment.is_deleted,
            replies=[]
        )
        for comment in comments
    ]


@router.delete("/{comment_id}")
async def hard_delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    success = service.hard_delete_comment_admin(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Comment permanently deleted"}