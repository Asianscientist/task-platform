import json
import redis

from app.config import get_settings

settings = get_settings()
client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_task(task_id: str):
    client.rpush(settings.queue_name, json.dumps({"task_id": task_id}))


def queue_length() -> int:
    return client.llen(settings.queue_name)


def pop_task(timeout: int = 5):
    item = client.blpop(settings.queue_name, timeout=timeout)
    if not item:
        return None
    return json.loads(item[1])
