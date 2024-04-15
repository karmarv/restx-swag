

import json, os
import logging
import datetime
import pandas as pd
import numpy as np
import urllib, cv2
import boto3 

log = logging.getLogger("rx")


#
# Assets: In-memory Datastore
#
s3_bucket, s3_store_files_df = None, None


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