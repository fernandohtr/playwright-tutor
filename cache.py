import redis.asyncio as redis

client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
)
