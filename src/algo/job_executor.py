
import time
import os


# ------------ #
# Setup/Config #
# ------------ #
log_worker_path = str(os.getenv('APP_LOG_PATH', "/tmp/restx/logs/"))
os.makedirs(log_worker_path, exist_ok=True)
""" 
    Print the log with timestamp 
"""
def pprint(log_text, log_type="INFO", log_name="JQ"):
    print("[{}] [{}][{}] - {}".format(time.strftime("%Y-%m-%dT%H:%M:%S"), log_name, log_type, log_text))


# ------------ #
#  Entrypoint  #
# ------------ #

def run(job_id, job_metadata):
    """
    Main entry point for analytics (Detection or MBSP)
    
    - Log to file and SQL job_id
    - Download input video, image and Upload result files to accessible location
    """
    # Job State - Start
    log_str = "{} - Job started; ".format(time)
    try:
        # Job Execute
        # Step 1: Wrap algorithm & execute as a sync process
        pprint("Execute worker job with metadata --> {}".format(job_metadata))
        # Step 2: log status update in database
        log_str = log_str + "{} - Initiate {}; ".format(time, job_metadata)
    except Exception as e:
        # Job Error: log exceptions and status in database
        log_str = "{} - Failure {}; ".format(time, repr(e))
        pprint(log_str, "ERROR")
        raise e
    finally:
        # Job Cleanup
        log_str = log_str + "{} - Job Completed; ".format(time)
        pprint("Finally verify results --> {}".format(job_id))

    # Job State - End
    return job_metadata
