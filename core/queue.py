"""
Redis Queue helpers — enqueue submission processing jobs.
"""

from redis import Redis
from rq import Queue

from core.config import settings


def get_redis_connection() -> Redis:
    return Redis.from_url(settings.REDIS_URL)


def get_queue() -> Queue:
    return Queue(settings.REDIS_QUEUE_NAME, connection=get_redis_connection())


def enqueue_submission(submission_token: str) -> str:
    """
    Enqueue a submission for async processing.
    Returns the RQ job id.
    """
    q = get_queue()
    job = q.enqueue("worker.process_submission", submission_token)
    return job.id
