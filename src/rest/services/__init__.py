from flask import Flask
from flask_restx import Api

from .sample_service import api as ns_ss


api = Api(version='1.0', 
          title='Flask RESTX API',
          description='A Flask RESTX API with Swagger for Sample data query')

# ------------------------ #
# Namespace configuration  #
# ------------------------ #
api.add_namespace(ns_ss)