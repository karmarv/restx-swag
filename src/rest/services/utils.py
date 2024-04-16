

import json, os
import logging
import time
import pandas as pd
import numpy as np
import urllib, cv2
import boto3 

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


# ------------------------------------ #
#   Images: Read S3 bucket Datastore   #
# ------------------------------------ #
def list_s3_metadata(prefix='rdd2020/retrain/'):
    """ Initialize the Asset data """
    start = time.time()
    # Setup AWS Bucket for files
    s3 = boto3.resource(
        service_name='s3',
        region_name=config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS,
        aws_secret_access_key=config.AWS_SECRET
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


""" Load image from a local path """
def load_image(image_fullPath, storage_type):
    try:
        log.info("Read: {}, Storage Type: {}".format(image_fullPath, storage_type))
        if storage_type == 'local':
            image = cv2.imread(image_fullPath)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else: # S3 lookup
            if "http" in image_fullPath:
                req = urllib.request.urlopen(image_fullPath)
                image = np.asarray(bytearray(req.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            else:
                obj = s3_bucket.Object(image_fullPath).get()
                image = np.asarray(bytearray(obj.get('Body').read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)           
        log.info("Read image shape: {}".format(image.shape))
        return image
    except Exception as e:
        log.error(e)
    return None

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
