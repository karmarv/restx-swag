import os
import logging
import pandas as pd

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from werkzeug.datastructures import FileStorage


from flask import make_response
from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse

from rest.services import config, utils
from rest.services.auth_service import token_required
import rest.services.data.image_metadata as dbmodel

log = logging.getLogger("rx")
api = Namespace('images', description='Operations related to Image data')


# -------------------------------------- #
# API Controllers and query param parser #
# -------------------------------------- #

reqp_ib_up = reqparse.RequestParser()
reqp_ib_up.add_argument('file', location='files', default=None, required=False, type=FileStorage, help='Uploaded form-data image file. Eg: jpg, jpeg, png files')
#reqp_up.add_argument('filename',  type=str,  default=None,   required=False, help='Full image path in AWS S3 bucket data. Eg: rdd2020/train/Czech/images/Czech_000010.jpg OR https://mmm-data.s3-us-west-2.amazonaws.com/rdd2020/train/Czech/images/Czech_000006.jpg')
reqp_ib_up.add_argument('overwrite', type=bool, default=False, required=False, help='Overwrite uploaded file if exists')

reqp_ib_qr = reqparse.RequestParser()
reqp_ib_qr.add_argument('name',        type=str, default=None, required=False, help='(Eg: .png) Download one image file object upon substring match in images table')



@api.route('/blob')
class ImageBlob(Resource):
    @api.expect(reqp_ib_qr)
    def get(self):
        """Returns image blob based on name substring match. `Unauthenticated` for search purposes. Set the Response content type to `image/jpeg` for image download link."""
        try:
            args = reqp_ib_qr.parse_args()
            #data = dbmodel.read_image_metadata(args.get('name'))
            filename = args.get('name')
            filepath = utils.find_file(filename)
            log.info("Found: {}".format(filepath))
            if filepath is None: 
                return "Unable to find " + filename, 404

            return {"directory":os.path.dirname(filepath), "filename": os.path.basename(filepath)}
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")

    @api.expect(reqp_ib_up)
    @token_required
    def post(self, current_user):
        """Uploads a new file to the flask server."""
        try:
            args = reqp_ib_up.parse_args()
            file = args.get('file')
            if file and utils.allowed_file(file.filename):
                file_path = utils.locate_savefile(file)
                data = dbmodel.create_image_metadata(file_path, content="local", overwrite=args.get('overwrite'))
                response = make_response(data)
                response.mimetype = "application/json"
                return response
            else:
                return "Unable to upload " + file.filename, 400
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")  
       


reqp_md_qr = reqparse.RequestParser()
reqp_md_qr.add_argument('name',        type=str, default=None, required=False, help='(Eg: .png) Filter files list by name substring from images table')
reqp_md_qr.add_argument('offset',      type=int, default=0,      required=False, help="(0) Starting index of the response")
reqp_md_qr.add_argument('limit',       type=int, default=100,    required=False, help="Maximum size of the response. limit=0 for querying all dataset")

reqp_md_up = reqparse.RequestParser()
reqp_md_up.add_argument('file',        type=str, default=None, required=False, help='full path to be entered as metadata to images table')
reqp_md_up.add_argument('overwrite',   type=bool, default=False,  required=False, help='Overwrite uploaded file metadata if exists')

@api.route('/metadata')
class ImageMetadata(Resource):
    @api.expect(reqp_md_qr)
    def get(self):
        """List image metadata based on name substring match. `Unauthenticated` for search purposes"""
        try:
            args = reqp_md_qr.parse_args()
            data = dbmodel.read_image_metadata_by_name(args.get('name'))
            response = make_response(data)
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")

    @api.expect(reqp_md_up)
    @token_required
    def post(self, current_user):
        """Create a new image metadata entry."""
        try:
            args = reqp_md_up.parse_args()
            file_path = args.get('file')
            if file_path and utils.allowed_file(file_path):
                data = dbmodel.create_image_metadata(file_path, content="local", overwrite=args.get('overwrite'))
                response = make_response(data)
                response.mimetype = 'application/json'
                return response
            else:
                return "Unable to upload " + file_path, 400
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")  

@api.route('/metadata/<string:image_id>')
class ImageMetadataItem(Resource):
    @token_required
    def get(self, image_id, current_user):
        """Fetch an image metadata. image_id must exist in database"""
        try:
            data = dbmodel.read_image_metadata(image_id)
            response = make_response(data)
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")       

    @token_required
    def delete(self, image_id, current_user):
        """Delete an image metadata entry"""
        dbmodel.del_image_metadata(image_id)
        return

