import os
import pathlib
from datetime import datetime

# Application configurations
APP_RELEASE_NAME = "Job Management Services"
APP_RELEASE_VERSION = "v0.1"
APP_DEPLOYMENT_PATH = str(os.getenv('APP_DEPLOYMENT_PATH', os.path.join(pathlib.Path(__file__).parent.absolute(),"..","..","..")))

# AWS Configuration: TODO Put in environment
AWS_REGION_NAME = os.environ.get('region_name', 'us-west-2')
AWS_ACCESS_KEY  = os.environ.get('aws_access_key_id', 'x')
AWS_SECRET_KEY  = os.environ.get('aws_secret_access_key', 'x')

# Flask Server State
SERVER_START_TIME = datetime.now()

# Redis Job management functions
REDIS_URL         = os.getenv("REDIS_URL", "redis://0.0.0.0:6379/0")
REDIS_QUEUES      = ["default"]
REDIS_JOB_PREFIX  = "job"
REDIS_JOB_STATUS  = ["enqueued", "started", "running", "finished", "error"]
REDIS_JOB_TIMEOUT = 3600*8   # 08 Hours - Each worker job timeout as handled by RQ
REDIS_JOB_TTL     = 3600*24  # 24 Hours - RQ result state information time to live 


# Formats
FORMAT_DATE="%Y-%m-%d"
FORMAT_TIME="%H:%M:%S"
FORMAT_DATETIME="%Y-%m-%dT%H:%M:%S"


# Data files
DATASTORE_FILES_ROOT = os.path.join(APP_DEPLOYMENT_PATH, "data")
SQLALCHEMY_DATABASE_PATH =  os.path.join(DATASTORE_FILES_ROOT, 'database.db')

# Sample Service Data
SAMPLE_DATA_CSV = os.path.join(DATASTORE_FILES_ROOT, "data_samples.csv")

# Image Service
IMAGES_S3_BUCKET_NAME = 'sample-data'
IMAGES_ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}
IMAGES_UPLOAD_FOLDER = os.path.join(DATASTORE_FILES_ROOT, "uploads")

