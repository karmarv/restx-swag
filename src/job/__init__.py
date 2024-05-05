from flask import Flask, Blueprint, request
from flask_restx import Api

# -------------------------- #
#  Initialize the Namespace  #
# -------------------------- #
from job.services.job_service import api as ns_jobs

blueprint_v1 = Blueprint("api", __name__, url_prefix="/api/v1") # Blueprint not included due to error

api = Api(blueprint_v1, 
          version='1.0', 
          title='Analytics Job queue with Redis <https://python-rq.org>',
          description='An unauthenticated job execution web services')

api.add_namespace(ns_jobs)