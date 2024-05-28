
import os
import json
import uuid
import logging

import redis
from rq import Queue, Connection
from rq import get_current_job
from rq import Callback
from rq.job import Job

from job.services import config

log = logging.getLogger("job")

def report_success(job, connection, result, *args, **kwargs):
    """Success callback upon completion of Job. This context is executed by the worker so does not have SQL database connection objects"""
    key = "rq:results:json:{}".format(job.id)
    connection.set(key, json.dumps(result, default=str), ex=60)
    pass

def report_failure(job, connection, type, value, traceback):
    """Failure callback upon error of Job. This context is executed by the worker so does not have SQL database connection objects"""
    key = "rq:results:failed:{}".format(job.id)
    connection.set(key, str(traceback.format_exc()), ex=60)
    pass

def submit_job(metadata):
    """ 
    Submit job to the Redis task queue for processing and persist the job state in KV store 
    """
    try:
        log.info("Submit: {}".format(metadata))
        job_id = str(metadata['id'])
        job_queue = str(metadata['queue'])
        job_module = str(metadata['module'])
        with Connection(redis.from_url(config.REDIS_URL)):
            q = Queue(job_queue)
            rqjob = q.enqueue(job_module, metadata, 
                                   job_id=job_id, 
                                   #job_timeout=config.REDIS_JOB_TIMEOUT,
                                   #result_ttl=config.REDIS_JOB_TTL,
                                   on_success=Callback(report_success), # default callback timeout (60 seconds) 
                                   on_failure=Callback(report_failure, timeout=10), # 10 seconds timeout
                                   )
        log.info("Submitted Job: {}".format(rqjob))
    except Exception as e:
        log.error("Job submission error. "+repr(e))
        raise Exception("ERROR: Unable to submit Job !\n{}".format(metadata))
    return 

def get_job_status(job_id):
    """
    List all the tasks in queue for execution
    """
    log.info("Query job id: {}".format(job_id))
    if job_id:
        with Connection(redis.from_url(config.REDIS_URL)) as conn:
            # Get redis jobs
            job = Job.fetch(id=job_id, connection=conn)
            log.info('Status: {}, Job: {}'.format(job.get_status(), job))

            # Get additional logs from database store
            # Job State - Start
            log_debug = "None"
            log_fail  = "None"
            jobs_data = { 
                          "status"                : job.get_status(),
                          "time_created"          : job.created_at.strftime(config.FORMAT_DATETIME) if job.created_at is not None else None,
                          "time_updated"          : job.ended_at.strftime(config.FORMAT_DATETIME) if job.ended_at is not None else None,
                          "failureReason"         : log_fail if log_fail is not None else None,
                          "log"                   : log_debug if log_debug is not None else None
                          }
            # Check Results 
            result = job.latest_result()

            log.info('Result: {}'.format(result.return_value))
            log.info('Result: {}'.format(result))
            if result.type == result.Type.SUCCESSFUL: 
                jobs_data["results"] = result.return_value
            else: 
                jobs_data["results"] = result.exc_string
    else:
        log.info("[TODO] Query all jobs")
        jobs_data = {}
    return jobs_data


def is_redis_available():
    """ 
    Test Redis connectivity from web services 
    """
    try:
        log.info("Testing connection to redis at {}".format(config.REDIS_URL))
        r = redis.from_url(config.REDIS_URL)
        r.ping()
        log.info("Successfully connected to redis at {}".format(config.REDIS_URL))
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        log.error("Redis connection error. ")
        raise Exception("ERROR: Initialize and configure Redis properly !")
    return True

is_redis_available()