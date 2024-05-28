
import os
import json
import time
import requests



# ------------ #
# Setup/Config #
# ------------ #
REDIS_JOB_STATUS  = ["enqueued", "started", "running", "finished", "error"]

log_worker_path = str(os.getenv('APP_LOG_PATH', "/tmp/restx/logs/"))
os.makedirs(log_worker_path, exist_ok=True)


""" 
    Print the log with timestamp 
"""
def pprint(log_text, log_type="INFO", log_name="JQ"):
    print("[{}] [{}][{}] - {}".format(time.strftime("%Y-%m-%dT%H:%M:%S"), log_name, log_type, log_text))

def get_search_results(keystring):
    params = {"q": "{}".format(keystring), "format": "json", "pretty": 1,"no_html": 1, "skip_disambig": 1}
    ddgurl = "https://api.duckduckgo.com"
    response = requests.get(url=ddgurl, params=params).json()
    return response

# ------------ #
#  Entrypoint  #
# ------------ #

def run(job_metadata):
    """
    Main entry point for analytics (Detection or MBSP)
    
    - Log to file and SQL job_id
    - Download input video, image and Upload result files to accessible location
    """
    # Job State - Start
    job_id = job_metadata["id"]
    job_metadata["status"] = REDIS_JOB_STATUS[1]
    log_str = "{} - {} Job started  ".format(time, job_id)
    try:
        # Job Execute

        # Step 1: Wrap algorithm & execute as a sync process
        pprint("Execute worker job with metadata --> {}".format(job_metadata))
        job_metadata["result"] = get_search_results(job_metadata["data"])

        # Step 2: log status update in database
        job_metadata["status"] = REDIS_JOB_STATUS[2]
        log_str = log_str + "{} - Initiate {}; ".format(time, job_metadata)
    except Exception as e:
        # Job Error: log exceptions and status in database
        job_metadata["status"] = REDIS_JOB_STATUS[4]
        log_str = "{} - Failure {}; ".format(time, repr(e))
        pprint(log_str, "ERROR")
        raise e

    # Job Cleanup
    job_metadata["status"] = REDIS_JOB_STATUS[3]
    log_str = log_str + "{} - Job Completed; ".format(time)
    pprint("Job {} --> {}".format(job_id, job_metadata["result"]))

    # Job State - End
    # Update metadata with results information
    job_metadata["time_updated"] = "{}".format(time)

    #data_json = json.dumps(job_metadata)
    return job_metadata["result"]
