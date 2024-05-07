import os
import logging
from dotenv import load_dotenv

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask
from flask_cors import CORS


from flask.logging import default_handler
from logging.config import dictConfig

from rest import db, blueprint_v1
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
            'filename': "../../logs/restx-api.log",
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


# ------------------------ #
# Application Launch Conf  #
# ------------------------ #
def create_app():
    """ Create the flask application """
    app = Flask(__name__)
    app.register_blueprint(blueprint_v1)  
    CORS(app)
    log.info('Initializing flask web application (App)')
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = config.IMAGES_UPLOAD_FOLDER
    
    # Configure the SQLite database and initialize Database Plugin
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SECRET_KEY"]     = config.JWT_SECRET_KEY
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["DEBUG"]          = True

    db.init_app(app)
    with app.app_context():
        # Create tables for our models
        db.create_all()    
    return app

## Api 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
