import os
import pathlib

# App configs
APP_DEPLOYMENT_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(),"..","..","..")

# AWS Configuration 

# Formats
FORMAT_DATE="%Y-%m-%d"
FORMAT_TIME="%H:%M:%S"
FORMAT_DATETIME="%Y-%m-%dT%H:%M:%S"


# Data flat files
DATASTORE_FILES_ROOT = os.path.join(APP_DEPLOYMENT_PATH, "data")

# Sample Service Data
SAMPLE_DATA_CSV = os.path.join(DATASTORE_FILES_ROOT, "data_samples.csv")

# Asset Service
ASSET_IMG_S3_BUCKET_NAME = 'sample-data'
ASSET_IMG_ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}
ASSET_IMG_UPLOAD_FOLDER = os.path.join(DATASTORE_FILES_ROOT, "uploads")
