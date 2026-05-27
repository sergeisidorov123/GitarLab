from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, author_id: int, author_username: str, comment_data: CommentCreate) -> Comment:
        comment = Comment(
            content=comment_data.content,
            author_id=author_id,
            author_username=author_username,
            track_id=comment_data.track_id,
            parent_id=comment_data.parent_id,
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments_by_track(self, track_id: str, include_deleted: bool = False) -> List[Comment]:
        query = self.db.query(Comment).filter(Comment.track_id == track_id)
        if not include_deleted:
            query = query.filter(Comment.is_deleted == False)
        return query.order_by(Comment.created_at).all()

    def get_comment_by_id(self, comment_id: int, include_deleted: bool = False) -> Optional[Comment]:
        query = self.db.query(Comment).filter(Comment.id == comment_id)
        if not include_deleted:
            query = query.filter(Comment.is_deleted == False)
        return query.first()

    def update_comment(self, comment_id: int, comment_data: CommentUpdate) -> Optional[Comment]:
        comment = self.get_comment_by_id(comment_id, include_deleted=True)
        if comment and not comment.is_deleted:
            comment.content = comment_data.content
            self.db.commit()
            self.db.refresh(comment)
            return comment
        return None

    def soft_delete_comment(self, comment_id: int) -> bool:
        comment = self.get_comment_by_id(comment_id, include_deleted=True)
        if comment and not comment.is_deleted:
            comment.is_deleted = True
            self.db.commit()
            return True
        return False

    def hard_delete_comment(self, comment_id: int) -> bool:
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False

    def get_all_comments(self, include_deleted: bool = False) -> List[Comment]:
        query = self.db.query(Comment)
        if not include_deleted:
            query = query.filter(Comment.is_deleted == False)
        return query.order_by(Comment.created_at.desc()).all()

    def get_comments_by_author(self, author_id: int, include_deleted: bool = False) -> List[Comment]:
        query = self.db.query(Comment).filter(Comment.author_id == author_id)
        if not include_deleted:
            query = query.filter(Comment.is_deleted == False)
        return query.order_by(Comment.created_at.desc()).all()