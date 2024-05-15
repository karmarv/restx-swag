import os
import logging
import time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from datetime import datetime
from flask import make_response, request
from flask_restx import Namespace, Resource

from job.services import config

log = logging.getLogger("job")
api = Namespace('stat', description='Operations related to server status and health')



@api.route('/ping')
class StatPing(Resource):
    def get(self):
        """Ping server state and diagnostic info """
        try:
            data = { "type"       : config.APP_RELEASE_NAME,
                     "version"    : config.APP_RELEASE_VERSION,
                     "status"     : "Server uptime - {}".format(datetime.now() - config.SERVER_START_TIME),
                     "serverTime" : time.strftime(config.FORMAT_DATETIME),
                     "userAgent"  : request.user_agent.string,
                     "cpuCount"   : os.cpu_count(),
                     "clientAddr" : request.remote_addr
                    }
            log.info(data)
            response = make_response(data)
            response.mimetype = 'application/json'
        except Exception as e:
            log.error("Could not retrieve information. "+repr(e))
            api.abort(500, e.__doc__, status = "Could not retrieve information. "+repr(e), statusCode = "500")  
        return response