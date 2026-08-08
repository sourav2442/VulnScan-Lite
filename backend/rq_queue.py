from redis import Redis
from rq import Queue


redis_connection = Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=False
)


scan_queue = Queue(
    "vulnscan",
    connection=redis_connection,
    default_timeout=120
)