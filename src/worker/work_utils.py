import os
import json



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