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
        "id"    : fields.String(required=True, description="Primary key job identifier"),
        "module": fields.String(required=True, description="Job execution module name with function specification"),
        "queue" : fields.String(required=True, description="Job queue selection and algorithm to be executed"),
        "data"  : fields.String(required=True, description="Data corresponding to this job run"),
        "path"  : fields.String(required=True, description="Path where results can be made available"),
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
parser.add_argument("module", type=str, required=True, location="form", default="worker.algo_search.run",  help="Specify the job handler python module name with function specification. Eg: module `worker.job_executor.run`")
parser.add_argument("queue",  type=str, required=True, location="form", default="rq_algorun",              help="Determines the job queue selection. Options: `rq_algorun`, `rq_algo_count`, `rq_algo_detect`")
parser.add_argument("data",   type=str, required=True, location="form", default="gaussian",                help="job data aassociated with the execution request. Options: String keywords, Serialized Json")
parser.add_argument("path",   type=str, required=True, location="form", default="/tmp/restx/results/",     help="job path where result can be made available on server")

       

@api.route("/async/<string:job_id>")
class Job(Resource):
    """Retrieve a single job item and status"""
    @api.marshal_with(job_meta)
    def get(self, job_id):
        """Fetch a given resource. job_id must exist in database"""
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
    """List of all jobs from metadata table"""
    @api.marshal_list_with(job_meta)
    def get(self):
        """List all jobs"""
        data = dbmodel.read_job_metadata()
        return data
    
    @api.expect(parser)
    @api.marshal_with(job_meta)
    def post(self):
        """Submit a job request for processing"""
        args = parser.parse_args()
        job_new = dbmodel.create_job_metadata(args.get('module'), args.get('queue'),
                                           args.get('data'), args.get('path'))
        job_manager.submit_job(job_new)
        return job_new

