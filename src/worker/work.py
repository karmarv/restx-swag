import os
import sys

from redis import Redis
from rq import Queue, Worker
from rq.serializers import JSONSerializer

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Preload libraries: https://python-rq.org/docs/workers/#performance-notes


if __name__ == "__main__":

    redis = Redis()

    # Start a worker with a custom name
    worker = Worker(['default','rq_algorun'], connection=redis, serializer=JSONSerializer, name='work_rq_algorun') # 
    worker.work()