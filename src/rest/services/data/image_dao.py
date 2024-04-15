import time, os
import logging
import pandas as pd
import boto3 

from rest.services import config 
from rest.services.data import database 


log = logging.getLogger("rx")

# ------------------------- #
# Configure the Data Utils  #
# ------------------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.IMAGES_ALLOWED_EXTENSIONS


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