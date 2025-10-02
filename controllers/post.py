from factory import api, db
from sqlalchemy import select
from flask import Blueprint, request
from spectree import Response
from pydantic import BaseModel

from flask_jwt_extended import current_user, jwt_required

from models.post import Post, PostCreate, PostResponse, PostResponseList
from utils.responses import DefaultResponse


posts_controller = Blueprint("posts_controller", __name__, url_prefix="/posts")


POSTS_PER_PAGE = 5


class SearchModel(BaseModel):
    search: str = ""
    page: int = 1
    reversed: bool = False


@posts_controller.get("/")
@api.validate(
    query=SearchModel,
    resp=Response(HTTP_200=PostResponseList),
    security={},
    tags=["posts"],
)
def get_all():
    """
    Get all posts
    """
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    reversed = True if request.args.get("reversed", "false") == "true" else False

    posts_query = select(Post).filter(Post.text.ilike(f"%{search}%"))

    if reversed:
        posts_query = posts_query.order_by(Post.created.desc())

    posts_pagination = db.paginate(
        posts_query,
        page=page,
        per_page=POSTS_PER_PAGE,
        error_out=False,
    )

    pages = posts_pagination.pages
    total = posts_pagination.total
    posts = posts_pagination.items

    response = PostResponseList(
        page=page,
        pages=pages,
        total=total,
        posts=[PostResponse.model_validate(post).model_dump() for post in posts],
    ).model_dump()

    return response, 200


@posts_controller.get("/<int:post_id>")
@api.validate(
    resp=Response(HTTP_200=PostResponse, HTTP_404=DefaultResponse), tags=["posts"]
)
@jwt_required()
def get_one(post_id):
    """
    Get one post
    """

    post = db.session.get(Post, post_id)

    if not post:
        return {"msg": "This post does not exists."}, 404

    response = PostResponse.model_validate(post).model_dump()
    return response, 200


@posts_controller.post("/")
@api.validate(json=PostCreate, resp=Response(HTTP_201=DefaultResponse), tags=["posts"])
@jwt_required()
def create_post():
    """
    Create post
    """

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
    """
    Update a post
    """

    post = db.session.get(Post, post_id)

    if post is None:
        return {"msg": "This post does not exists."}, 404

    if not (post.author_id == current_user.id or current_user.role.can_manage_posts):
        return {"msg": "You can't change this post."}, 403

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
    """
    Delete a post
    """

    post = db.session.get(Post, post_id)

    if post is None:
        return {"msg": "This post does not exists."}, 404

    if not (post.author_id == current_user.id or current_user.role.can_manage_posts):
        return {"msg": "You can't delete this post."}, 403

    db.session.delete(post)
    db.session.commit()

    return {"msg": "The post was deleted."}, 200
