
import os
import time
import uuid
import logging

import redis
from rq import Queue, Connection
from rq import get_current_job
from rq.job import Job

from job.services import config
from job.services.job_executor import run_job

log = logging.getLogger("app")


def submit_job(model):
    """ 
    Submit job to the Redis task queue for processing and persist the job state in KV store 
    """
    try:
        job_id = "{}:{}".format(os.path.basename(model['videoInputPath']), str(uuid.uuid4()))
        with Connection(redis.from_url(config.REDIS_URL)):
            q = Queue()
            job = q.enqueue(run_job, job_id, 
                                        model['azureStorageCredentials'], 
                                        model['videoInputPath'], 
                                        model['videoOutputPath'], 
                                        job_id=job_id, 
                                        job_timeout=config.REDIS_JOB_TIMEOUT,
                                        result_ttl=config.REDIS_JOB_TTL)

        # Add this job to the redis data store Hash structure
        with redis.Redis.from_url(url=config.REDIS_URL) as r:
            db_key = "{}:{}".format(config.REDIS_JOB_PREFIX, job_id)
            key_exists = r.exists(db_key) 
            model['jobId']         = job_id
            model['status']        = config.REDIS_JOB_STATUS[0]
            model['jobStartTime']  = ""
            model['jobFinishTime'] = ""
            model['jobSubmissionTime'] = time.strftime(config.FORMAT_DATETIME) 
            result = r.hmset(db_key, model)
        log.info("Submitted Job: {}".format(model))
    except Exception as e:
        log.error("Job submission error. "+repr(e))
        raise Exception("ERROR: Unable to submit Job !")
    return


def get_job_status(job_id, offset, limit):
    """
    List all the tasks in queue for execution
    """
    log.info("Query job id: {}".format(job_id))
    if job_id:
        with Connection(redis.from_url(config.REDIS_URL)) as conn:
            # Get redis jobs
            job = Job.fetch(job_id, connection=conn)
            log.info('Status: {}, Job: {}'.format(job.get_status(), job))

            # Get additional logs from database Hash store
            with redis.Redis.from_url(url=config.REDIS_URL) as r:
                db_key = "{}:{}".format(config.REDIS_JOB_PREFIX, job_id)
                if not r.exists(db_key):
                    raise Exception("ERROR: Unable to process Job - {}. Not found in Redis Database !".format(db_key))

                # Job State - Start
                log_debug = r.hget(db_key, 'log')
                log_fail  = r.hget(db_key, 'error')

            jobs_data = { "jobId"                 : job_id,
                          "status"                : job.get_status(),
                          "progress"              : "",
                          "operationStartTime"    : job.created_at.strftime(config.FORMAT_DATETIME) if job.created_at is not None else None,
                          "operationFinishTime"   : job.ended_at.strftime(config.FORMAT_DATETIME) if job.ended_at is not None else None,
                          "failureReason"         : log_fail.decode() if log_fail is not None else None,
                          "log"                   : log_debug.decode() if log_debug is not None else None
                          #"arguments"             : job.args
                          }
            """
            # Check Results 
            for result in job.results(): 
                print(result.created_at, result.type)
                if result == result.Type.SUCCESSFUL: 
                    log.info(result.return_value) 
                else: 
                    log.info(result.exc_string)
            """
    else:
        log.info("[TODO] Query all jobs")
        jobs_data = {}
    return jobs_data


def is_redis_available():
    """ 
    Test Redis connectivity from web services 
    """
    try:
        r = redis.from_url(config.REDIS_URL)
        r.ping()
        log.info("Successfully connected to redis at {}".format(config.REDIS_URL))
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        log.error("Redis connection error. ")
        raise Exception("ERROR: Initialize and configure Redis properly !")
    return True

is_redis_available()