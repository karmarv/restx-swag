import time, os
import logging
import pandas as pd

from rest.services import config 

log = logging.getLogger("rx")

# ------------------------- #
# Configure the Data Utils  #
# ------------------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ASSET_IMG_ALLOWED_EXTENSIONS


# ------------------------------------ #
# Samples: Load the In-memory Datastore #
# ------------------------------------ #
def init_sample_data():
    start = time.time()
    # Sample Data
    df_sample = pd.read_csv(config.SAMPLE_DATA_CSV)
    df_sample["Datetime"] = pd.to_datetime(df_sample["Time"]) # format="%Y%m%d%H%M%S", utc=True
    # Create a DatetimeIndex and assign it to the dataframe.
    df_sample.index = pd.DatetimeIndex(df_sample["Datetime"])
    end = time.time()
    log.info("-------------- Read Sample Data ({} rows, {:.2f} sec) --------------".format(len(df_sample), (end - start)))
    print("Logs are being written to (project-dir)/logs/*.log files")
    return df_sample

