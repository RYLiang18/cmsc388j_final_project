# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_talisman import Talisman
from flask_mail import Mail
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
# stdlib
from datetime import datetime
import os


db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()




def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(dict(
        DEBUG = True,
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
        MAIL_USERNAME = 'flaskmemories@gmail.com',
        MAIL_PASSWORD = 'badPassword',
        MAIL_DEFAULT_SENDER='flaskmemories@gmail.com'
        ))
    mail = Mail(app)

    csp = {
        'default-src': ['\'self\'',
        '\'unsafe-inline\'',
        'stackpath.bootstrapcdn.com',
        'code.jquery.com',
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com'],
        'img-src': ['self', 'data:'],
    }
    talisman = Talisman(app, content_security_policy=csp)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)


    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # %%%%%%%%% REGISTERING BLUEPRINTS %%%%%%%%%
    from flask_app.users.routes import users
    from flask_app.photos.routes import photos

    app.register_blueprint(users)
    app.register_blueprint(photos)
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"






    return app
