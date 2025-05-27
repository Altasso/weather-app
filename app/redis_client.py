import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "test_ocomplex-redis-1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
