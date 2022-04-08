import os

from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SecurityScheme, SpecTree

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = SpecTree(
    "flask",
    title="Mini Feed API",
    version="v.1.0",
    path="docs",
    security_schemes=[
        SecurityScheme(
            name="api_key",
            data={"type": "apiKey", "name": "Authorization", "in": "header"},
        )
    ],
    security={"api_key": []},
)


Flask.jinja_options = {"variable_start_string": "%%", "variable_end_string": "%%"}


def create_app(ConfigClass):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.getcwd(), "templates"),
        static_folder=os.path.join(os.getcwd(), "static"),
    )

    app.config.from_object(ConfigClass)

    CORS(app, supports_credentials=True)

    jwt.init_app(app)
    db.init_app(app)

    from models import Post, User

    migrate.init_app(app, db)

    from models import User

    @jwt.user_lookup_loader
    def user_load(token, data):
        current_user = User.query.filter_by(username=data["sub"]).first()

        return current_user

    @app.route("/")
    def home():
        return render_template("index.html")

    from controllers import auth_controller, posts_controller, user_controller

    app.register_blueprint(auth_controller)
    app.register_blueprint(user_controller)
    app.register_blueprint(posts_controller)

    api.register(app)

    return app
