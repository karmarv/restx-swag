import logging
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import make_response
from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse

from job.services import config, utils

log = logging.getLogger("job")
api = Namespace('jobs', description='Operations related to Async/Sync job execution service')


# -------------------------------------- #
# API Controllers and query param parser #
# -------------------------------------- #
reqp_md_qr = reqparse.RequestParser()
reqp_md_qr.add_argument('name',        type=str, default=None, required=False, help='(Eg: .png) Filter files list by name substring from images table')
reqp_md_qr.add_argument('offset',      type=int, default=0,      required=False, help="(0) Starting index of the response")
reqp_md_qr.add_argument('limit',       type=int, default=100,    required=False, help="Maximum size of the response. limit=0 for querying all dataset")

reqp_md_up = reqparse.RequestParser()
reqp_md_up.add_argument('file',        type=str, default=None, required=False, help='full path to be entered as metadata to images table')
reqp_md_up.add_argument('overwrite',   type=bool, default=False,  required=False, help='Overwrite uploaded file metadata if exists')

@api.route('/async')
class JobAsync(Resource):
    @api.expect(reqp_md_qr)
    def get(self):
        """Returns list of jobs"""
        try:
            args = reqp_md_qr.parse_args()
            data = {"message": "TODO"} #dbmodel.read_image_metadata(args.get('name'))
            response = make_response(data)
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")

    @api.expect(reqp_md_up)
    def post(self):
        """Create a new job request"""
        try:
            args = reqp_md_up.parse_args()
            file_path = args.get('file')
            if file_path and utils.allowed_file(file_path):
                data = {} #dbmodel.create_image_metadata(file_path, content="local", overwrite=args.get('overwrite'))
                response = make_response(data)
                response.mimetype = 'application/json'
                return response
            else:
                return "Unable to create " + file_path, 400
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")  
       