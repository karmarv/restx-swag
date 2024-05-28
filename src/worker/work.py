import os
import sys

import redis
from rq import Worker, Queue, Connection

# Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


# Preload libraries: https://python-rq.org/docs/workers/#performance-notes


if __name__ == "__main__":
    # Redis connection URL
    redis_url = os.getenv("REDIS_URL", "redis://0.0.0.0:6379/0")
    # Queue this worker is listening to
    listen = ['default','rq_algorun']
    # Connect to redis for jobs
    with Connection(redis.from_url(redis_url)):
        # Start a worker with a custom name
        worker = Worker(list(map(Queue, listen)), name='work_rq_algorun')
        worker.work()
