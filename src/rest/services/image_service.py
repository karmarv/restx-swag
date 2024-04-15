import json, os
import logging
import sys, time
import datetime
import pandas as pd

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask import Flask, Response, jsonify, make_response
from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from flask.logging import default_handler

from rest.services import config
import rest.services.data.image_dao as images

log = logging.getLogger("rx")
api = Namespace('images', description='Operations related to Image data')

#
# Initialize the Sqlite Datastore
#




# -------------------------------------- #
# Parsers: Upload, Filter and Pagination #
# -------------------------------------- #
reqp_up = reqparse.RequestParser()
reqp_up.add_argument('file', location='files', default=None, required=False, type=FileStorage, help='Uploaded form-data image file. Eg: jpg, jpeg, png files')
reqp_up.add_argument('filename', type=str, default=None, required=False, help='Full image path in AWS S3 bucket mmm-data. Eg: rdd2020/train/Czech/images/Czech_000010.jpg OR https://mmm-data.s3-us-west-2.amazonaws.com/rdd2020/train/Czech/images/Czech_000006.jpg')

reqp_qr = reqparse.RequestParser()
reqp_qr.add_argument('name',        type=str, default=None, required=False, help='(Eg: Czech_00001)Filter files list by name substring')
reqp_qr.add_argument('segment_id',  type=str, default=None,     required=False, help='(Eg: 1510) Demand segmentation id relating to a polygon on map.')
reqp_qr.add_argument('offset',      type=int, default=0,      required=False, help="(0) Starting index of the response")
reqp_qr.add_argument('limit',       type=int, default=100,    required=False, help="Maximum size of the response. limit=0 for querying all dataset")


@api.route('/')
class ImageList(Resource):
    @api.expect(reqp_qr)
    def get(self):
        # test: https://mmm-data.s3-us-west-2.amazonaws.com/rdd2020/train/Czech/images/Czech_000010.jpg
        """Returns list of asset image link based on name substring match."""
        try:
            args = reqp_qr.parse_args()
            data = images.list(name_filter=args.get('name'),
                                segment_id=args.get('segment_id'),
                                offset=args.get('offset'),
                                limit=args.get('limit'))
            response = make_response(data.to_json(orient='split'))
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")

    @api.expect(reqp_up)
    def post(self):
        """Uploads a new file to the flask server."""
        try:
            args = reqp_up.parse_args()
            file = args.get('file')
            filenames3 = args.get('filename')
            if file and allowed_file(file.filename):
                log.info(file.filename)
                filename = secure_filename(file.filename)
                file.save(os.path.join(config.ASSET_IMG_UPLOAD_FOLDER, filename))
                bboxes = detect_damages(image_path=os.path.join(config.ASSET_IMG_UPLOAD_FOLDER, filename), storage_type='local')
                response = make_response(bboxes.to_json(orient='split'))
                response.mimetype = 'application/json'
                return response
            elif filenames3 and allowed_file(filenames3):
                bboxes = detect_damages(image_path=filenames3, storage_type='s3')
                response = make_response(bboxes.to_json(orient='split'))
                response.mimetype = 'application/json'
                return response
            else:
                return "Unable to upload " + file.filename, 400
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")  
       



@api.route('/kpis')
class KpiList(Resource):
    @api.doc('get_kpi')
    def get(self):
        """Returns list of KPI data sample grouped by 'Severity' column."""
        try:
            data = fetch_kpis()
            response = make_response(data.to_json(orient='split'))
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")