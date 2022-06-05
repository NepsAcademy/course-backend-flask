import json
import math

from factory import api, db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from models.post import Post, PostCreate, PostResponse, PostResponseList
from pydantic import BaseModel
from spectree import Response
from utils.responses import DefaultResponse

posts_controller = Blueprint("posts_controller", __name__, url_prefix="/posts")


@posts_controller.post("/")
@api.validate(json=PostCreate, resp=Response(HTTP_201=DefaultResponse), tags=["posts"])
@jwt_required()
def create_post():
    """Create post"""

    data = request.json

    post = Post(text=data["text"], author_id=current_user.id)

    db.session.add(post)
    db.session.commit()

    return {"msg": f"Post with id {post.id} created."}, 201


@posts_controller.put("/<int:post_id>")
@api.validate(
    json=PostCreate,
    resp=Response(
        HTTP_200=DefaultResponse, HTTP_403=DefaultResponse, HTTP_404=DefaultResponse
    ),
    tags=["posts"],
)
@jwt_required()
def update(post_id):
    """Update a post"""

    post = Post.query.get(post_id)

    if post is None:
        return {"msg": "This post does not exists."}, 404

    if not (post.author_id == current_user.id or current_user.role.can_manage_posts):
        return {"msg": "You can only change your own posts."}, 403

    data = request.json

    post.text = data["text"]

    db.session.commit()

    return {"msg": "The post was updated."}, 200


@posts_controller.delete("/<int:post_id>")
@api.validate(
    resp=Response(
        HTTP_200=DefaultResponse, HTTP_403=DefaultResponse, HTTP_404=DefaultResponse
    ),
    tags=["posts"],
)
@jwt_required()
def delete(post_id):
    """Delete a post"""

    post = Post.query.get(post_id)

    if post is None:
        return {"msg": "This post does not exists."}, 404

    if not (post.author_id == current_user.id or current_user.role.can_manage_posts):
        return {"msg": "You can't delete this post."}, 403

    db.session.delete(post)
    db.session.commit()

    return {"msg": "The post was deleted."}, 200


@posts_controller.get("/<int:post_id>")
@api.validate(
    resp=Response(HTTP_200=PostResponse, HTTP_404=DefaultResponse),
    security={},
    tags=["posts"],
)
def get_one(post_id):
    """Get one post"""

    post = Post.query.get(post_id)

    if post:
        response = PostResponse.from_orm(post).json()

        return json.loads(response), 200

    return {"msg": "This post does not exists."}, 404


class SearchModel(BaseModel):
    search: str = ""
    page: int = 1
    reversed: bool = False


POSTS_PER_PAGE = 5

# Get all
@posts_controller.route("/", methods=["GET"])
@api.validate(
    query=SearchModel,
    resp=Response(HTTP_200=PostResponseList),
    security={},
    tags=["posts"],
)
def get_all():
    """Get all posts"""

    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    reversed = True if request.args.get("reversed", "false") == "true" else False

    posts_query = Post.query.filter(Post.text.ilike(f"%{search}%"))

    if reversed:
        posts_query = posts_query.order_by(Post.created.desc())

    posts_pagination = posts_query.paginate(page, POSTS_PER_PAGE)

    total, posts = posts_pagination.total, posts_pagination.items

    response = PostResponseList(
        page=page,
        pages=math.ceil(total / POSTS_PER_PAGE),
        total=total,
        posts=[PostResponse.from_orm(post).dict() for post in posts],
    ).json()

    return jsonify(json.loads(response)), 200
