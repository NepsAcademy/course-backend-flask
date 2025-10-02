from factory import db
from utils.models import OrmBase


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)

    can_access_sensitive_information = db.Column(db.Boolean, default=False)
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_posts = db.Column(db.Boolean, default=False)

    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class RoleResponse(OrmBase):
    name: str
    can_access_sensitive_information: bool
    can_manage_users: bool
    can_manage_posts: bool
