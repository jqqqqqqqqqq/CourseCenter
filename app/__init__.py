from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_uploads import UploadSet, configure_uploads, patch_request_class

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
ups = UploadSet('files', extensions=('xls', 'xlsx'))


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    configure_uploads(app, ups)
    patch_request_class(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

