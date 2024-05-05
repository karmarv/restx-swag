
import jwt

from flask import Flask, Blueprint, send_from_directory
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
from rest.services.exceptions import ValidationException
from rest.services.auth_service import api as ns_au
from rest.services.image_service import api as ns_is

blueprint_v1 = Blueprint("api", __name__, url_prefix="/api/v1") # Blueprint not included due to error

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(blueprint_v1,
          version='1.0', 
          title='Platform Webservices with JWT security',
          description='A Flask RESTX API with Swagger, JWT and SQLAlchemy integration', 
          security='Bearer Auth',
          authorizations=authorizations)



@api.errorhandler(ValidationException)
def handle_validation_exception(error):
    return {'message': 'Validation error', 'errors': {error.error_field_name: error.message}}, 400

@api.errorhandler(jwt.ExpiredSignatureError)
def handle_expired_signature_error(error):
    return {'message': 'Token expired', 'errors': str(error)}, 401

@api.errorhandler(jwt.InvalidTokenError)
@api.errorhandler(jwt.DecodeError)
@api.errorhandler(jwt.InvalidIssuerError)
def handle_invalid_token_error(error):
    return {'message': 'Token incorrect, supplied or malformed', 'errors': str(error)}, 401

api.add_namespace(ns_au)
api.add_namespace(ns_is)


# Custom response based on response content type for images
@api.representation('image/png')
def output_image(data, code, headers):
    return send_from_directory(data["directory"], data["filename"], as_attachment=True)

@api.representation('image/jpeg')
def output_image(data, code, headers):
    return send_from_directory(data["directory"], data["filename"], as_attachment=True)
