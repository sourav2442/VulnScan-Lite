from redis import Redis
from rq import Queue

from test_tasks import test_job


redis_connection = Redis(
    host="localhost",
    port=6379,
    db=0
)

queue = Queue(
    "vulnscan",
    connection=redis_connection
)

job = queue.enqueue(test_job)

print("Job queued successfully!")
print("Job ID:", job.id)