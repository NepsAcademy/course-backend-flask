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


@user_controller.route("/", methods=["GET"])
@api.validate(resp=Response(HTTP_200=UserResponseList), tags=["users"])
@jwt_required()
def get_users():
    """
    Get all users
    """

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

    user = User.query.get(user_id)

    if user is None:
        return {"msg": f"There is no user with id {user_id}"}, 404

    response = UserResponse.from_orm(user).json()

    return json.loads(response), 200


@user_controller.route("/<int:user_id>", methods=["PUT"])
@api.validate(
    json=UserResponse,
    resp=Response(HTTP_200=DefaultResponse),
    tags=["users"],
)
@jwt_required()
def put_user(user_id):
    """
    Update an user
    """

    user = User.query.get(user_id)

    if user is None:
        return {"msg": f"There is no user with id {user_id}"}, 404

    if user.id != current_user.id:
        return {"msg": "You can only change you own information."}, 403

    data = request.json

    # Update user

    user.username = data["username"]
    user.email = data["email"]

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

    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return {"msg": "User deleted from the database."}, 200


@user_controller.route("/", methods=["POST"])
@api.validate(json=UserCreate, resp=Response(HTTP_201=DefaultResponse), security={}, tags=["users"])
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
