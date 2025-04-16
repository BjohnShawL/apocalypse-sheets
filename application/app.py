import os
import secrets
import sqlite3

from devtools import debug
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from application.models import *
from application.extensions import db
from application.views import main, playbooks


def create_app():
    flask_app = Flask(__name__)
    create_new_data = os.environ.get('ADD_DATA') == 'True'
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "mariadb+mariadbconnector://root:root@127.0.0.1:3306/sheets"
    bootstrap = Bootstrap(flask_app)
    csrf = CSRFProtect(flask_app)
    secret_key = secrets.token_urlsafe(32)
    flask_app.secret_key = secret_key

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)

    flask_app.register_blueprint(main)
    flask_app.register_blueprint(playbooks)
    return flask_app


def add_data():
    chosen = Playbook(name="The Chosen",
                      description="Your birth was prophesied. You are the Chosen One, and with your abilities you can "
                                  "save the world. If you fail, all will be destroyed. It all rests on you. Only you.")

    db.session.add(chosen)
    destiny_plaything = Move(name="Destiny's Plaything",
                             description="At the beginning of each mystery, roll +Weird to see what is revealed about "
                                         "your immediate future. On a 10+, the Keeper will reveal a useful detail "
                                         "about the coming mystery. On a 7-9 you get a vague hint about it. On a "
                                         "miss, something bad is going to happen to you.", playbook_id=chosen.id)
    db.session.add(destiny_plaything)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()

    app.run()
