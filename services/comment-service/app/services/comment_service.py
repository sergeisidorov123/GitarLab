import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repos.comment_repo import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.models.comment import Comment


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommentRepository(db)

    def create_comment(self, author_id: int, author_username: str, comment_data: CommentCreate) -> Comment:
        # Validate parent comment exists if provided
        if comment_data.parent_id:
            parent = self.repo.get_comment_by_id(comment_data.parent_id)
            if not parent:
                raise ValueError("Parent comment not found")
            if parent.track_id != comment_data.track_id:
                raise ValueError("Parent comment must be on the same track")

        return self.repo.create_comment(author_id, author_username, comment_data)

    def get_comments_for_track(self, track_id: str) -> List[CommentResponse]:
        comments = self.repo.get_comments_by_track(track_id)

        # Build comment tree
        comment_map = {}
        root_comments = []

        for comment in comments:
            comment_response = CommentResponse(
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
            comment_map[comment.id] = comment_response

            if comment.parent_id:
                if comment.parent_id in comment_map:
                    comment_map[comment.parent_id].replies.append(comment_response)
            else:
                root_comments.append(comment_response)

        return root_comments

    def update_comment(self, comment_id: int, author_id: int, comment_data: CommentUpdate) -> Optional[Comment]:
        comment = self.repo.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        if comment.author_id != author_id:
            raise ValueError("Not authorized to edit this comment")

        return self.repo.update_comment(comment_id, comment_data)

    def delete_comment(self, comment_id: int, author_id: int, is_admin: bool = False) -> bool:
        comment = self.repo.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        if not is_admin and comment.author_id != author_id:
            raise ValueError("Not authorized to delete this comment")

        return self.repo.soft_delete_comment(comment_id)

    def get_all_comments_for_admin(self) -> List[Comment]:
        return self.repo.get_all_comments(include_deleted=True)

    def hard_delete_comment_admin(self, comment_id: int) -> bool:
        return self.repo.hard_delete_comment(comment_id)