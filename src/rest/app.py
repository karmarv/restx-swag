import json, os
import logging
import sys

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, Response, jsonify, make_response
from flask_cors import CORS
from flask_restx import Api, Resource, reqparse

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

# -------------------------- #
# Initialize the Application #
# -------------------------- #
from rest.services import api
def create_app():
    """ Create the flask application """
    app = Flask(__name__)
    CORS(app)
    log.info('Initializing flask web application')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.app_context().push()
    api.init_app(app)
    return app

## Api 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
