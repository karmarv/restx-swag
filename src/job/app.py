import os
import jwt
import logging
from dotenv import load_dotenv

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, Blueprint, request
from flask_restx import Api
from flask_cors import CORS

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
            'filename': "../../logs/restx-jobs.log",
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

log = logging.getLogger("job")
os.makedirs("../../logs", exist_ok=True)
logging.config.dictConfig(dict_config)
load_dotenv()  # take environment variables from .env.



# -------------------------- #
#  Initialize the Namespace  #
# -------------------------- #
from job.services.job_service import api as ns_js

api_bp = Blueprint("api", __name__, url_prefix="/api/v1") # Blueprint not included due to error
api = Api(version='1.0', 
          title='Job web-service',
          description='An unauthenticated job execution web services')

api.add_namespace(ns_js)


# ------------------------ #
# Application Launch Conf  #
# ------------------------ #
def create_app():
    """ Create the flask application """
    app = Flask(__name__)
    CORS(app)
    log.info('Initializing flask web application (App)')
    # Configure the app
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    app.config["DEBUG"]              = True

    app.app_context().push()
    api.init_app(app)
    #app.register_blueprint(api_bp) # Blueprint not included due to error
    return app

## Api 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001)
