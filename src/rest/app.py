import json, os
import logging
from dotenv import load_dotenv

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, Response, jsonify, make_response
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


from flask.logging import default_handler
from logging.config import dictConfig

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
# Initialize the Application #
# -------------------------- #
from rest.services import api
def create_app():
    """ Create the flask application """
    app = Flask(__name__)
    CORS(app)
    log.info('Initializing flask web application (App)')
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    
    # Configure the SQLite database and initialize Database Plugin
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/database.db"
    db.init_app(app)
    with app.app_context():
        from rest.services import image_service
        # Create tables for our models
        db.create_all()
        
    app.app_context().push()
    api.init_app(app)
    return app

## Api 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
