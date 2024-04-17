import os
import jwt
import logging
from dotenv import load_dotenv

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, Blueprint, request
from flask_restx import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from flask.logging import default_handler
from logging.config import dictConfig

from rest.services import config 

# ------------ #
# Setup Logger #
# ------------ #
dict_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "../../logs/restx-swag.log",
            'maxBytes': 5000000,
            'backupCount': 10
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },
    'loggers': {
        'rx': {
            'handlers': ["default"],
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ["default", "console"],
        'level': 'INFO',
    },
}

log = logging.getLogger("rx")
os.makedirs("../../logs", exist_ok=True)
logging.config.dictConfig(dict_config)
load_dotenv()  # take environment variables from .env.

# -------------------------- #
# Initialize Database Model  #
# -------------------------- #
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)


# -------------------------- #
#  Initialize the Namespace  #
# -------------------------- #
from rest.services.exceptions import ValidationException
from rest.services.auth_service import api as ns_au
from rest.services.image_service import api as ns_is

api_bp = Blueprint("api", __name__, url_prefix="/api/v1") # Blueprint not included due to error
api = Api(version='1.0', 
          title='Flask RESTX API',
          description='A Flask RESTX API with Swagger for Sample data query')

@api.errorhandler(ValidationException)
def handle_validation_exception(error):
    return {'message': 'Validation error', 'errors': {error.error_field_name: error.message}}, 400

@api.errorhandler(jwt.ExpiredSignatureError)
def handle_expired_signature_error(error):
    return {'message': 'Token expired', 'errors': str(error)}, 401

@api.errorhandler(jwt.InvalidTokenError)
@api.errorhandler(jwt.DecodeError)
@api.errorhandler(jwt.InvalidIssuerError)
def handle_invalid_token_error(error):
    return {'message': 'Token incorrect, supplied or malformed', 'errors': str(error)}, 401

api.add_namespace(ns_au)
api.add_namespace(ns_is)


# ------------------------ #
# Application Launch Conf  #
# ------------------------ #
def create_app():
    """ Create the flask application """
    app = Flask(__name__)
    CORS(app)
    log.info('Initializing flask web application (App)')
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    
    # Configure the SQLite database and initialize Database Plugin
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + config.SQLALCHEMY_DATABASE_PATH
    app.config["SECRET_KEY"]     = config.JWT_SECRET_KEY
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["DEBUG"]          = True

    db.init_app(app)
    with app.app_context():
        # Create tables for our models
        db.create_all()
    
    app.app_context().push()
    api.init_app(app)
    #app.register_blueprint(api_bp) # Blueprint not included due to error
    return app

## Api 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
