from flask import Flask, Blueprint, request
from flask_restx import Api

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# -------------------------- #
# Initialize Database Model  #
# -------------------------- #
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# -------------------------- #
#  Initialize the Namespace  #
# -------------------------- #
from job.services.exceptions import JobException
from job.services.job_service import api as ns_jobs
from job.services.stat_service import api as ns_stat

blueprint_v1 = Blueprint("api", __name__, url_prefix="/api/v1") # Blueprint not included due to error

api = Api(blueprint_v1, 
          version='1.0', 
          title='Analytics Job with Redis Queue',
          description='An unauthenticated backend job execution web services')


@api.errorhandler(JobException)
def handle_job_exception(error):
    return {'message': 'Job error', 'errors': {error.error_field_name: error.message}}, 400

api.add_namespace(ns_jobs)
api.add_namespace(ns_stat)
