from datetime import datetime, timezone
from pydantic import BaseModel

from factory import db
from utils.models import OrmBase
from models.user import UserResponseSimple


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    text = db.Column(db.UnicodeText)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship("User", back_populates="posts")

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
    posts: list[PostResponse]
