from datetime import datetime
from typing import List

from factory import db
from pydantic import BaseModel
from utils.models import OrmBase
from models.user import UserResponseSimple


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"<Post {self.id}>"


class PostCreate(BaseModel):
    text: str


class PostResponse(OrmBase):
    text: str
    created: datetime
    author: UserResponseSimple


class PostResponseList(BaseModel):
    page: int
    pages: int
    total: int
    posts: List[PostResponse]
