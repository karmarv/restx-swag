import logging
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restx import Namespace, Resource, fields


log = logging.getLogger("job")
api = Namespace('jobs', description='Operations related to Async/Sync job execution service')


# -------------------------------------- #
# Data Model and sample #
# -------------------------------------- #

job = api.model(
    "Job", 
    {
        "name": fields.String(required=True, description="Job name"),
        "type": fields.String(required=True, description="Algorithm to be executed"),
        "data": fields.String(required=True, description="Data corresponding to this job run"),
    }
)

job_list = api.model(
    "JobList",
    {
        "id": fields.String(required=True, description="The job identifier"),
        "job": fields.Nested(job, description="Job description"),
    },
)

# TODO - Move this to a SQL database
JOBS = {
    "job11": { "name": "build an API", "type": "MBSP"},
    "job22": { "name": "?????", "type": "Count", "data":"http://1.bp.blogspot.com/--M8WrSToFoo/VTVRut6u-2I/AAAAAAAAB8o/dVHTtpXitSs/s1600/URL.png"},
    "task3": { "name": "profit!", "type": "Count"},
}

def abort_if_todo_doesnt_exist(job_id):
    if job_id not in JOBS:
        api.abort(404, "Job {} doesn't exist".format(job_id))



# -------------------------------------- #
# API Controllers and query param parser #
# -------------------------------------- #

parser = api.parser()
parser.add_argument(
    "job", type=str, required=True, help="The job details", location="form"
)
       

@api.route("/async/<string:job_id>")
@api.doc(responses={404: "Todo not found"}, params={"job_id": "The Job identifier"})
class Job(Resource):
    """Show a single job item and lets you delete them"""

    @api.doc(description="job_id should be in {0}".format(", ".join(JOBS.keys())))
    @api.marshal_with(job)
    def get(self, job_id):
        """Fetch a given resource"""
        abort_if_todo_doesnt_exist(job_id)
        return JOBS[job_id]

    @api.doc(responses={204: "Todo deleted"})
    def delete(self, job_id):
        """Delete a given resource"""
        abort_if_todo_doesnt_exist(job_id)
        del JOBS[job_id]
        return "", 204

    @api.doc(parser=parser)
    @api.marshal_with(job)
    def put(self, job_id):
        """Update a given resource"""
        args = parser.parse_args()
        task = {"name": args["job"]}
        JOBS[job_id] = task
        return task


@api.route("/async")
class JobList(Resource):
    """Shows a list of all jobs"""
    @api.marshal_list_with(job_list)
    def get(self):
        """List all jobs"""
        return [{"id": id, "job": job} for id, job in JOBS.items()]
