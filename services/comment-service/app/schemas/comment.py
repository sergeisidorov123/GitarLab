from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator


class CommentBase(BaseModel):
    content: str
    track_id: str

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty')
        if len(v.strip()) > 1000:
            raise ValueError('Comment content cannot exceed 1000 characters')
        return v.strip()


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty')
        if len(v.strip()) > 1000:
            raise ValueError('Comment content cannot exceed 1000 characters')
        return v.strip()


class CommentResponse(CommentBase):
    id: int
    author_id: int
    author_username: str
    parent_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List['CommentResponse'] = []

    class Config:
        orm_mode = True


CommentResponse.update_forward_refs()


class CommentAdminResponse(CommentResponse):
    is_deleted: bool

    class Config:
        orm_mode = True