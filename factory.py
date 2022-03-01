from flask import Flask, render_template
from config import Config

from flask_sqlalchemy import SQLAlchemy

from spectree import SpecTree, SecurityScheme

from flask_jwt_extended import JWTManager

from flask_cors import CORS
import jinja2.ext

from utils import fix_spectree_layout

db = SQLAlchemy()
api = SpecTree(
    "flask",
    path="docs",
    title="Mini Feed",
    version="0.5.0",
    mode="strict",
    security_schemes=[
        SecurityScheme(
            name="api_key",
            data={"type": "apiKey", "name": "Authorization", "in": "header"},
        )
    ],
    security={"api_key": []},
)

jwt = JWTManager()

Flask.jinja_options = {"variable_start_string": "%%", "variable_end_string": "%%"}


def create_app():

    import os

    app = Flask(
        __name__,
        template_folder=os.path.join(os.getcwd(), "templates"),
        static_folder=os.path.join(os.getcwd(), "static"),
    )

    app.config.from_object(Config)

    jwt.init_app(app)
    db.init_app(app)

    fix_spectree_layout()  # This is a patch to change the layout of the spectree swagger UI

    CORS(app)

    from models import User

    @jwt.user_lookup_loader
    def user_load(token, data):
        current_user = User.query.filter_by(username=data["sub"]).first()

        return current_user

    @app.route("/")
    def home():
        return render_template("index.html")

    from controllers import user_controller, posts_controller, auth_controller

    app.register_blueprint(auth_controller)
    app.register_blueprint(user_controller)
    app.register_blueprint(posts_controller)

    api.register(app)

    return app
