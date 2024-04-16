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

from rest.services import config, utils
from rest.services.data.model import db, Image, Serializer

log = logging.getLogger("rx")
api = Namespace('images', description='Operations related to Image data')

# Create an entry into the image metadata database
def create_entry(fullpath, content):
    new_img = None
    if fullpath:
        new_img = Image(
            fullpath=fullpath,
            content=content,
        )  # Create an instance of the Image class
        db.session.add(new_img)     # Adds new User record to database
        db.session.commit()         # Commits all changes
    return new_img

# Locate and save to filesystem
def locate_save(file):
    log.info(file.filename)
    filename = secure_filename(file.filename)
    fullpath = os.path.join(config.IMAGES_UPLOAD_FOLDER, filename)
    file.save(fullpath)
    return fullpath

# -------------------------------------- #
# Parsers: Upload, Filter and Pagination #
# -------------------------------------- #
reqp_up = reqparse.RequestParser()
reqp_up.add_argument('file', location='files', default=None, required=False, type=FileStorage, help='Uploaded form-data image file. Eg: jpg, jpeg, png files')
reqp_up.add_argument('filename',  type=str,  default=None,   required=False, help='Full image path in AWS S3 bucket data. Eg: rdd2020/train/Czech/images/Czech_000010.jpg OR https://mmm-data.s3-us-west-2.amazonaws.com/rdd2020/train/Czech/images/Czech_000006.jpg')
reqp_up.add_argument('overwrite', type=bool, default=False,  required=False, help='Overwrite uploaded file if exists')


reqp_qr = reqparse.RequestParser()
reqp_qr.add_argument('name',        type=str, default=None, required=False, help='(Eg: Czech_00001)Filter files list by name substring')
reqp_qr.add_argument('offset',      type=int, default=0,      required=False, help="(0) Starting index of the response")
reqp_qr.add_argument('limit',       type=int, default=100,    required=False, help="Maximum size of the response. limit=0 for querying all dataset")


@api.route('/')
class ImageList(Resource):
    @api.expect(reqp_qr)
    def get(self):
        """Returns list of asset image link based on name substring match."""
        try:
            args = reqp_qr.parse_args()
            imgs = Image.query.all()
            response = make_response(Serializer.serialize_list(imgs))
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")

    @api.expect(reqp_up)
    def post(self):
        """Uploads a new file to the flask server."""
        try:
            args = reqp_up.parse_args()
            file = args.get('file')
            if file and utils.allowed_file(file.filename):
                fullpath = locate_save(file)
                existing_img = Image.query.filter(Image.fullpath == fullpath).first()
                if existing_img and not args.get('overwrite'):
                    response = make_response(existing_img.serialize())
                    print("Image already exists: ", existing_img)
                else:
                    data = create_entry(fullpath, content="local")
                    response = make_response(data.serialize())
                response.mimetype = 'application/json'
                return response
            else:
                return "Unable to upload " + file.filename, 400
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information"+str(e), statusCode = "400")  
       

