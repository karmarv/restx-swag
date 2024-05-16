import os
import logging
import time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from datetime import datetime
from flask import make_response, request, jsonify
from flask_restx import Namespace, Resource, fields, marshal

from job.services import config, job_manager
import job.services.data.job_metadata as dbmodel

log = logging.getLogger("job")
api = Namespace('jobs', description='Operations related to Async/Sync job execution service')


# -------------------------------------- #
# Data Model and sample #
# -------------------------------------- #

job_meta = api.model(
    "JobMetadata", 
    {
        "id"    : fields.String(required=True, description="The job identifier"),
        "name"  : fields.String(required=True, description="Job name"),
        "type"  : fields.String(required=True, description="Algorithm to be executed"),
        "data"  : fields.String(required=True, description="Data corresponding to this job run"),
        "path"  : fields.String(required=True, description="Path where to lookup this data"),
        "status": fields.String(required=True, description="Status of this job run"),
        "result": fields.String(required=False, description="Result of this job run"),
        "time_created": fields.String(required=False, description="Job created time"),
        "time_updated": fields.String(required=False, description="Job completion/update time")
    }
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
    @api.marshal_with(job_meta)
    def get(self, job_id):
        """Fetch a given resource"""
        data = dbmodel.read_job_metadata(id=job_id)
        results = job_manager.get_job_status(job_id)
        data["status"] = results["status"]
        data["result"] = results["results"]
        data["time_created"] = results["time_created"]
        data["time_updated"] = results["time_updated"]
        log.info(results) 
        return data


@api.route("/async")
class JobList(Resource):
    """Shows a list of all jobs"""
    @api.marshal_list_with(job_meta)
    def get(self):
        """List all jobs"""
        data = dbmodel.read_job_metadata()
        return data
    
    @api.doc(parser=parser)
    @api.marshal_with(job_meta)
    def post(self):
        """Create a given resource"""
        args = parser.parse_args()
        job_new = dbmodel.create_job_metadata(args.get('name'), args.get('type'),
                                           args.get('data'), args.get('path'))
        job_manager.submit_job(job_new)
        return job_new

