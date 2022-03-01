from datetime import timedelta

from factory import api
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models import User
from pydantic import BaseModel
from spectree import Response
from utils.responses import DefaultResponse

auth_controller = Blueprint("auth_controller", __name__, url_prefix="/auth")


class LoginMessage(BaseModel):
    username: str
    password: str


class LoginResponseMessage(BaseModel):
    access_token: str


# Login
@auth_controller.route("/login", methods=["POST"])
@api.validate(
    json=LoginMessage, resp=Response(HTTP_200=LoginResponseMessage), security={}, tags=["auth"]
)
def login():
    """Login in the system"""

    data = request.json

    user = User.query.filter_by(username=data["username"]).first()

    if user and user.verify_password(data["password"]):
        return {
            "access_token": create_access_token(
                identity=user.username, expires_delta=None
            )
        }

    return {"msg": "Username and password do not match."}, 401


# Logout
@auth_controller.route("/logout", methods=["POST"])
@api.validate(json=LoginMessage, resp=Response(HTTP_200=DefaultResponse), tags=["auth"])
def logout():
    """Logout user"""
    return {"msg": "Logout successfully."}
