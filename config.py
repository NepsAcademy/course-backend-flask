import os

# basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.getcwd()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "Vp62aTffoX7CC@")

    APP_TITLE = "Full Stack Developer: Backend"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    # SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"].replace(
    #     "postgres", "postgresql"
    # )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "t5rbggFvME54t3D@")
    JWT_TOKEN_LOCATION = ["headers"]

    @staticmethod
    def init_app(app):
        pass
