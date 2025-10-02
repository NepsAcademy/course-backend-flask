from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select
from spectree import Response

from factory import api, db
from models.user import User, UserCreate, UserEdit, UserResponse, UserResponseList
from utils.responses import DefaultResponse


user_controller = Blueprint("user_controller", __name__, url_prefix="/users")


@user_controller.get("/me")
@api.validate(resp=Response(HTTP_200=UserResponse), tags=["users"])
@jwt_required()
def me():
    """
    Returns information about the current user
    """

    response = UserResponse.model_validate(current_user).model_dump()

    return response, 200


@user_controller.get("/")
@api.validate(resp=Response(HTTP_200=UserResponseList), tags=["users"])
@jwt_required()
def get_users():
    """
    Get all users
    """

    if not (current_user and current_user.role.can_manage_users):
        return {"msg": "You don't have permission to view all users."}, 403

    users = db.session.scalars(select(User)).all()

    response = UserResponseList(
        users=[UserResponse.model_validate(user).model_dump() for user in users]
    ).model_dump()

    return response, 200


@user_controller.get("/<int:user_id>")
@api.validate(
    resp=Response(HTTP_200=UserResponse, HTTP_404=DefaultResponse), tags=["users"]
)
@jwt_required()
def get_user(user_id):
    """
    Get a specified user
    """
    if not (current_user and current_user.role.can_access_sensitive_information):
        return {
            "msg": "You don't have permission to access this user information."
        }, 403

    user = db.session.get(User, user_id)

    if user is None:
        return {"msg": f"There is no user with id {user_id}"}, 404

    response = UserResponse.model_validate(user).model_dump()

    return response, 200


@user_controller.post("/")
@api.validate(
    json=UserCreate,
    resp=Response(HTTP_201=DefaultResponse),
    security={},
    tags=["users"],
)
def post_user():
    """
    Create an user
    """
    data = request.json

    if db.session.scalars(select(User).filter_by(username=data["username"])).first():
        return {"msg": "username not available"}, 409

    if "birthdate" in data:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]

    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        birthdate=(
            datetime.fromisoformat(data["birthdate"]) if "birthdate" in data else None
        ),
    )

    db.session.add(user)
    db.session.commit()

    return {"msg": "User created successfully."}, 201


@user_controller.put("/")
@api.validate(
    json=UserEdit,
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse),
    tags=["users"],
)
@jwt_required()
def put_user():
    """
    Update an user
    """
    user = current_user

    data = request.json

    user.username = data["username"]
    user.email = data["email"]

    if "birthdate" in data:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]
        user.birthdate = datetime.fromisoformat(data["birthdate"])

    db.session.commit()

    return {"msg": "User was updated."}, 200


@user_controller.delete("/<int:user_id>")
@api.validate(
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=["users"]
)
@jwt_required()
def delete_user(user_id):
    """
    Delete an user
    """

    if not (current_user and current_user.role.can_manage_users):
        return {"msg": "You don't have permission to delete this user."}, 403

    user = db.session.get(User, user_id)

    db.session.delete(user)
    db.session.commit()

    return {"msg": "User deleted from the database."}, 200
