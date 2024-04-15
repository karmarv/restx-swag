import os
import pathlib

# App configs
APP_DEPLOYMENT_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(),"..","..","..")

# AWS Configuration 
# TODO: Put in environment
AWS_REGION = os.environ.get('region_name', 'us-west-2')
AWS_ACCESS = os.environ.get('aws_access_key_id', 'x')
AWS_SECRET = os.environ.get('aws_secret_access_key', 'x')

# Formats
FORMAT_DATE="%Y-%m-%d"
FORMAT_TIME="%H:%M:%S"
FORMAT_DATETIME="%Y-%m-%dT%H:%M:%S"


# Data flat files
DATASTORE_FILES_ROOT = os.path.join(APP_DEPLOYMENT_PATH, "data")

# Sample Service Data
SAMPLE_DATA_CSV = os.path.join(DATASTORE_FILES_ROOT, "data_samples.csv")

# Image Service
IMAGES_S3_BUCKET_NAME = 'sample-data'
IMAGES_ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}
IMAGES_UPLOAD_FOLDER = os.path.join(DATASTORE_FILES_ROOT, "uploads")

