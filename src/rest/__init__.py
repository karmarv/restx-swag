import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask
from flask_cors import CORS

import logging
log = logging.getLogger("rx")

# -------------------------- #
# Initialize the Application #
# -------------------------- #
def create_app():
    app = Flask(__name__)
    CORS(app)
    from .services import api
    log.info('Initializing flask web application')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.app_context().push()
    api.init_app(app)
    return app

