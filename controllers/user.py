import json
from datetime import datetime

from factory import api, db
from flask import Blueprint, jsonify
from flask.globals import request
from flask_jwt_extended import current_user, jwt_required
from models.user import User, UserCreate, UserResponse, UserResponseList
from spectree import Response
from utils.responses import DefaultResponse

user_controller = Blueprint("user_controller", __name__, url_prefix="/users")


@user_controller.route("/me", methods=["GET"])
@api.validate(resp=Response(HTTP_200=UserResponse), tags=["users"])
@jwt_required()
def me():
    """Returns information about the current user"""

    response = UserResponse.from_orm(current_user).json()

    return json.loads(response), 200


@user_controller.route("/", methods=["GET"])
@api.validate(resp=Response(HTTP_200=UserResponseList), tags=["users"])
@jwt_required()
def get_users():
    """
    Get all users
    """

    if not (current_user and current_user.role.can_manage_users):
        return {"msg": "You don't have permission to view all users."}, 403

    users = User.query.all()

    response = UserResponseList(
        __root__=[UserResponse.from_orm(user).dict() for user in users]
    ).json()

    return jsonify(json.loads(response)), 200


@user_controller.route("/<int:user_id>")
@api.validate(resp=Response(HTTP_200=UserResponse, HTTP_404=None), tags=["users"])
@jwt_required()
def get_user(user_id):
    """
    Get a specified user
    """

    if not (current_user and current_user.role.can_access_sensitive_information):
        return {
            "msg": "You don't have permission to access this user information."
        }, 403

    user = User.query.get(user_id)

    if user is None:
        return {"msg": f"There is no user with id {user_id}"}, 404

    response = UserResponse.from_orm(user).json()

    return json.loads(response), 200


@user_controller.route("/", methods=["PUT"])
@api.validate(
    json=UserCreate,
    resp=Response(HTTP_200=DefaultResponse),
    tags=["users"],
)
@jwt_required()
def put_user():
    """
    Update the current user
    """

    user = User.query.get(current_user.id)

    data = request.json

    # Update user

    user.username = data["username"]
    user.email = data["email"]
    user.password = data["password"]

    if data["birthdate"]:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]

        user.birthdate = datetime.fromisoformat(data["birthdate"])

    db.session.commit()

    return {"msg": "User was updated."}, 200


@user_controller.route("/<int:user_id>", methods=["DELETE"])
@api.validate(resp=Response(HTTP_200=DefaultResponse), tags=["users"])
@jwt_required()
def delete_user(user_id):
    """
    Delete an user
    """

    if not (current_user and current_user.role.can_manage_users):
        return {"msg": "You don't have permission to delete this user."}, 403

    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return {"msg": "User deleted from the database."}, 200


@user_controller.route("/", methods=["POST"])
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

    if User.query.filter_by(username=data["username"]).first():
        return {"msg": "Username not available."}

    user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )

    if "birthdate" in data:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]

        user.birthdate = datetime.fromisoformat(data["birthdate"])

    db.session.add(user)
    db.session.commit()

    return {"msg": f"User with id {user.id} created successfully."}, 201
