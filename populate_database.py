"""
Populate database based on files "post.csv" and "users.csv"
"""
import os
import csv
from datetime import datetime
from textwrap import dedent

from factory import db
from main import app
from models import Post, User

URL = "http://127.0.0.1:5000"
basedir = os.path.abspath(os.path.dirname(__file__))

# Exception raised when an error occurs
class Error(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return dedent(
            f"""
            {self.message}.
            Sorry, something is wrong!
            Please let Neps know by emailing the error above to thiago@neps.academy or sending on Discord community.
            """
        )


def create_users(users):
    for user in users:
        new_user = User(
            username=user["username"],
            password=user["password"],
            email=user["email"],
            birthdate=datetime.fromisoformat(user["birthdate"]),
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating users.")


def create_posts(posts):
    for post in posts:
        new_post = Post(text=post["text"], author_id=post["author_id"])
        try:
            db.session.add(new_post)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating users.")


def main():
    resources_dir = os.path.join(basedir, "resources")

    with open(os.path.join(resources_dir, "users.csv"), "r") as users_file, open(
        os.path.join(resources_dir, "posts.csv"), "r"
    ) as posts_file, app.app_context():

        users = csv.DictReader(users_file)
        posts = csv.DictReader(posts_file)
    
        create_users(users)
        create_posts(posts)


if __name__ in "__main__":
    main()
