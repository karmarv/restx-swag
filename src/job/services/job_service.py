import os
import logging
import time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from datetime import datetime
from flask import make_response, request, jsonify
from flask_restx import Namespace, Resource, fields

from job.services import config, job_manager
import job.services.data.job_metadata as dbmodel

log = logging.getLogger("job")
api = Namespace('jobs', description='Operations related to Async/Sync job execution service')


# -------------------------------------- #
# Data Model and sample #
# -------------------------------------- #

job = api.model(
    "Job", 
    {
        "id"    : fields.String(required=True, description="The job identifier"),
        "name"  : fields.String(required=True, description="Job name"),
        "type"  : fields.String(required=True, description="Algorithm to be executed"),
        "data"  : fields.String(required=True, description="Data corresponding to this job run"),
        "path"  : fields.String(required=True, description="Path where to lookup this data"),
        "status": fields.String(required=True, description="Status of this job run"),
    }
)

job_list = api.model(
    "JobList",
    {
        "job": fields.Nested(job, description="Job description"),
    },
)


# -------------------------------------- #
# API Controllers and query param parser #
# -------------------------------------- #
parser = api.parser()
parser.add_argument("name", type=str, required=True, help="job name", location="form")
parser.add_argument("type", type=str, required=True, help="job type", location="form")
parser.add_argument("data", type=str, required=True, help="job data", location="form")
parser.add_argument("path", type=str, required=True, help="job path", location="form")

       

@api.route("/async/<string:job_id>")
@api.doc(responses={404: "Todo not found"}, params={"job_id": "The Job identifier"})
class Job(Resource):
    """Show a single job item and lets you delete them"""
    @api.doc(description="job_id must exist in database")
    @api.marshal_with(job)
    def get(self, job_id):
        """Fetch a given resource"""
        data = dbmodel.read_job_metadata(id=job_id)
        response = make_response(data)
        response.mimetype = 'application/json'
        return response


@api.route("/async")
class JobList(Resource):
    """Shows a list of all jobs"""
    @api.marshal_list_with(job_list)
    def get(self):
        """List all jobs"""
        data = dbmodel.read_job_metadata()
        response = make_response(data)
        response.mimetype = 'application/json'
        return response
    
    @api.doc(parser=parser)
    @api.marshal_with(job)
    def post(self):
        """Create a given resource"""
        args = parser.parse_args()
        job_manager.submit_job(job)
        job = dbmodel.create_job_metadata(args.get('name'), args.get('type'),
                                           args.get('data'), args.get('path'))
        
        
        print(job)
        response = make_response(job)
        response.mimetype = 'application/json'
        return response


@api.route('/ping')
class JobsPing(Resource):
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