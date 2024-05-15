
import time
import os
import redis

from app.services import config


# ------------ #
# Setup/Config #
# ------------ #
os.makedirs(config.APP_LOG_PATH, exist_ok=True)
""" 
    Print the log with timestamp 
"""
def pprint(log_text, log_type="INFO", log_name="JQ"):
    print("[{}] [{}][{}] - {}".format(time.strftime("%Y-%m-%dT%H:%M:%S"), log_name, log_type, log_text))

"""
    Input  : directory that needs creation
"""
def mkdir_exists(dirname):
    if not os.path.isdir(dirname):
        try:
            os.makedirs(dirname, exist_ok = True)
        except OSError as error:
            pprint("Directory {} can not be created. {}".format(dirname, error), "ERROR")
            raise error
    return


# ------------ #
#  Entrypoint  #
# ------------ #

def run_job(job_id, conn_str, blob_in_url, blob_out_url):
    """
    Main entry point for frame reduction evaluations (Stationary -> Anomaly -> Binary)
    
    - Log to file and Redis job_id based hash value set
    - Download input video and Upload result files as Blob using connection_string
    """

    """
    Algorithm Execution
    """
    pprint("Execute flow analysis on {}".format(blob_prop["path"]))
    try:
        # Stationary - Feature extraction, Classification & Redis log update
        stationary_stat_file, stationary_span_file, _ = stationary_executor.run(blob_prop["path"], 
                                                            output_dir = config.get_data_base_path("root"),
                                                            # Process Flow Features
                                                            skip_frames     = config.STAT_SAMPLE_RATE_FPS_VALUE,
                                                            hash_type       = "phash",
                                                            hash_size       = 8,
                                                            grid_size       = (9,9),
                                                            # Estimate thresholds
                                                            sample_block    = (3,3),
                                                            band_pass_mean  = config.STAT_FILTER_BANDPASS_MEAN,
                                                            band_pass_width = config.STAT_FILTER_BANDPASS_WIDTH,
                                                            pad_threshold   = config.STAT_FILTER_PAD_THRESHOLD
                                                            )
        log_str = log_str + "{} - Stationary Classification {}; ".format(time.strftime(config.FORMAT_DATETIME), stationary_span_file)
        r.hset(db_key, 'log', log_str)
    except Exception as e:
        r.hset(db_key, 'status', config.REDIS_JOB_STATUS[-1])
        r.hset(db_key, 'error', repr(e))
        pprint(repr(e), "ERROR")
        raise e

    # Upload - Blob video file to output URL and Redis log update
    pprint("Upload stationary results to blob storage. Results: {}, {}".format(stationary_stat_file, stationary_span_file))
    result_stat_blob_url = "{}{}".format(blob_out_url, os.path.basename(stationary_stat_file))
    result_blob_prop = put_blob(conn_str, None, stationary_stat_file, result_stat_blob_url)
    result_span_blob_url = "{}{}".format(blob_out_url, os.path.basename(stationary_span_file))
    result_blob_prop = put_blob(conn_str, None, stationary_span_file, result_span_blob_url)
    pprint("Blob uploaded to {}".format(result_blob_prop["path"]))
    log_str = log_str + "{} - Stationary Results {}; ".format(time.strftime(config.FORMAT_DATETIME), result_blob_prop["path"])
    r.hset(db_key, 'log', log_str)

    # Job State - Cleanup
    if os.path.isfile(blob_prop["path"]):
        # Remove videos from local download path
        os.remove(blob_prop["path"])
        pprint("Cleanup video data at {}".format(blob_prop["path"]))

    # Job State - End
    log_str = log_str + "{} - Job Completed; ".format(time.strftime(config.FORMAT_DATETIME))
    r.hset(db_key, 'log', log_str)
    r.hset(db_key, 'status', config.REDIS_JOB_STATUS[3])
    r.hset(db_key, 'jobFinishTime', time.strftime(config.FORMAT_DATETIME))

    return
