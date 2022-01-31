from flask import Flask , Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import logging
import sys
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask import jsonify

jwt = JWTManager()

# Set a callback function to return a custom response whenever an expired
    # token attempts to access a protected route. This particular callback function
    # takes the jwt_header and jwt_payload as arguments, and must return a Flask
    # response. Check the API documentation to see the required argument and return
    # values for other callback functions.
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify(status_code=401, message="Token is expired"), 401

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()


def create_app(config_class=Config):
    # Initialize logging
    logger = logging.getLogger()
    f = logging.Formatter('$asctime $levelname $message', style='$')
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(f)
    logger.addHandler(h)
    logger.setLevel(Config.log_level)
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        from models import User
        db.create_all()  # Create sql tables for our data models

    from admin.routes import admin
    from candidate.routes import candidate
    from api.V1 import v1
    from api.V2 import v2
    app.register_blueprint(v1)
    app.register_blueprint(v2)
    app.register_blueprint(admin)
    app.register_blueprint(candidate)

    CORS(app)

    # @app.route("/hello", methods=['GET', 'POST'])
    # def hello():
    #     return "Hello World"

    return app




