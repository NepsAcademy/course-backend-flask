from datetime import datetime
from typing import List

from factory import db
from pydantic import BaseModel
from utils.models import OrmBase
from werkzeug.security import check_password_hash, generate_password_hash

from models.role import Role, RoleResponse


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), index=True)

    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    birthdate = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            self.role = Role.query.filter_by(name="user").first()

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserEdit(BaseModel):
    username: str
    email: str
    birthdate: datetime = None


class UserCreate(UserEdit):
    password: str


class UserResponse(OrmBase):
    username: str
    email: str
    birthdate: datetime = None
    created_at: datetime
    role: RoleResponse


class UserResponseList(BaseModel):
    __root__: List[UserResponse]
