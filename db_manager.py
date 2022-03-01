import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from main import app
from factory import db

with app.app_context():

    from models import User

    migrate = Migrate(app, db)
    manager = Manager(app)

    manager.add_command("db", MigrateCommand)

    if __name__ == "__main__":
        manager.run()
