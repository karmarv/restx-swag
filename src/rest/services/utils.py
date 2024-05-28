

import os, fnmatch
import logging
import time
import pandas as pd
import numpy as np
import urllib, cv2
import boto3 

import jwt
from werkzeug.utils import secure_filename

from rest.services import config 


log = logging.getLogger("rx")


#
# Assets: In-memory Datastore
#
s3_bucket, s3_store_files_df = None, None


# ------------------------- #
# Configure the Data Utils  #
# ------------------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.IMAGES_ALLOWED_EXTENSIONS


# ----------------------------------- #
#   Images and data file processing   #
# ----------------------------------- #

""" Locate and save image to filesystem """ 
def locate_savefile(file, storage_type="local"):
    log.info("Store: {}, Storage Type: {}".format(file.filename, storage_type))
    filename = secure_filename(file.filename)
    fullpath = os.path.join(config.IMAGES_UPLOAD_FOLDER, filename)
    file.save(fullpath)
    return fullpath


""" Load file from a local path """
def find_file(filepath, storage_type="local"):
    log.info("Search: {}, Storage Type: {}".format(filepath, storage_type))
    if os.path.exists(filepath):
        return filepath
    elif os.path.exists(os.path.join(config.IMAGES_UPLOAD_FOLDER, filepath)):
        return os.path.join(config.IMAGES_UPLOAD_FOLDER, filepath)
    else:
        # find images in upload folder and return first match
        for root, dirs, files in os.walk(config.IMAGES_UPLOAD_FOLDER):
            for name in files:
                if fnmatch.fnmatch(name, filepath):
                    return os.path.join(root, name)
    return None

""" Load image from a local path """
def load_image(filepath, storage_type="local"):
    image = None
    log.info("Read: {}, Storage Type: {}".format(filepath, storage_type))
    if storage_type == "local":
        if os.path.exists(filepath):
            image = cv2.imread(filepath)    # read image from full file path
        else:
            image = cv2.imread(os.path.join(config.IMAGES_UPLOAD_FOLDER, filepath))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else: 
        if "http" in filepath:
            # URL from internet
            req = urllib.request.urlopen(filepath)
            image = np.asarray(bytearray(req.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            # S3 public bucket lookup
            obj = s3_bucket.Object(filepath).get()
            image = np.asarray(bytearray(obj.get('Body').read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)           
    log.info("Read image shape: {}".format(image.shape))
    return image

def list_s3_metadata(prefix='rdd2020/retrain/'):
    """ Initialize the Asset data """
    start = time.time()
    # Setup AWS Bucket for files
    s3 = boto3.resource(
        service_name='s3',
        region_name=config.AWS_REGION_NAME,
        aws_access_key_id=config.AWS_ACCESS_KEY,
        aws_secret_access_key=config.AWS_SECRET_KEY
    )
    s3_bucket = s3.Bucket(config.IMAGES_S3_BUCKET_NAME)
    s3_store_files = {}
    # Query contents of S3 bucket
    s3_files = list(s3_bucket.objects.filter(Prefix=prefix))
    for idx, item in enumerate(s3_files):
        #if (idx < 5):
        #    print("{}.) \t {} \t {}".format(idx, item, item.key))
        if allowed_file(item.key):
            s3_store_files[item.key] = item.bucket_name
    s3_store_files_df = pd.DataFrame({'asset':s3_store_files.keys(), 'bucket':s3_store_files.values()})
    end = time.time()
    log.info("-------------- Asset Service ({} sec, {} images) -------------- ".format((end - start), len(s3_store_files_df)))
    return s3_bucket, s3_store_files_df

""" Image list data access functions """
def list(name_filter, segment_id, offset=0, limit=25):
    global datastore_assessed_damage_df
    # 1. Filter by file_name 
    if name_filter is not None:
        filtered_df = datastore_assessed_damage_df[datastore_assessed_damage_df["url"].str.contains(name_filter.strip(), na=False)]
    else: 
        filtered_df = datastore_assessed_damage_df

    if segment_id is not None:
        filtered_df = filtered_df[filtered_df["segment_id"] == int(segment_id)]
    log.info("Queried: {}, Count {}".format(name_filter, len(filtered_df.index)))
    # Limit to a records subset
    if len(filtered_df.index) > 1 and limit > 0:
        filtered_df = filtered_df[offset:limit]
    #filtered_df.sort_values(by=['date', 'time'], ascending=[False, False], inplace=True)
    return filtered_df


