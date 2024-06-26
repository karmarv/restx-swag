import os
import pathlib

# Application configurations
APP_RELEASE_NAME = "App Services"
APP_RELEASE_VERSION = "v0.1"
APP_DEPLOYMENT_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(),"..","..","..")

# JWT and Security
JWT_SECRET_KEY = os.environ.get('jwt_secret_key', "top-secret-config")
JWT_ALGORITHM  = "HS256"
JWT_ACCESS_TOKEN_EXPIRY_MINUTES = 60 * 10   # 10 hours
JWT_REFRESH_TOKEN_EXPIRY_DAYS   = 30        # 30 days
# 4-16 symbols, can contain A-Z, a-z, 0-9, _ (_ can not be at the begin/end and can not go in a row (__))
JWT_USERNAME_REGEXP = r'^(?![_])(?!.*[_]{2})[a-zA-Z0-9._]+(?<![_])$'
# 6-64 symbols, required upper and lower case letters. Can contain !@#$%_  .
JWT_PASSWORD_REGEXP = r'^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])[\w\d!@#$%_]{6,64}$'


# AWS Configuration: TODO Put in environment
AWS_REGION_NAME = os.environ.get('region_name', 'us-west-2')
AWS_ACCESS_KEY  = os.environ.get('aws_access_key_id', 'x')
AWS_SECRET_KEY  = os.environ.get('aws_secret_access_key', 'x')

# Formats
FORMAT_DATE="%Y-%m-%d"
FORMAT_TIME="%H:%M:%S"
FORMAT_DATETIME="%Y-%m-%dT%H:%M:%S"


# Data files
DATASTORE_FILES_ROOT = os.path.join(APP_DEPLOYMENT_PATH, "data")
SQLALCHEMY_DATABASE_PATH =  os.path.join(DATASTORE_FILES_ROOT, 'database.db')
#SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///" + SQLALCHEMY_DATABASE_PATH)
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://restx:restx123@localhost:5432/restxdb")

# Sample Service Data
SAMPLE_DATA_CSV = os.path.join(DATASTORE_FILES_ROOT, "data_samples.csv")

# Image Service
IMAGES_S3_BUCKET_NAME = 'sample-data'
IMAGES_ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}
IMAGES_UPLOAD_FOLDER = os.path.join(DATASTORE_FILES_ROOT, "uploads")

