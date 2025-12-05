from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserSchema(BaseModel):
    email: str
    nickname: str
    profile: Optional[str] = None

    class Config:
        orm_mode = True


class CommentSchema(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


class PostListItemSchema(BaseModel):
    id: int
    title: str
    views: str
    comments: str
    likes: str
    created_at: str


class PostDetailSchema(BaseModel):
    id: int
    title: str
    content: str
    views: str
    likes: str
    comments_count: str
    liked: bool
    created_at: str

