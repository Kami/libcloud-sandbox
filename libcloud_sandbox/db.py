import redis

from libcloud_sandbox.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

def get_client():
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return client

def get_old_commands(key):
    client = get_client()
    length = client.llen(key)
    commands = client.lrange(key, 0, length)
    return commands

def write_code(key, code):
    client = get_client()
    return client.rpush(key, *code.split('\n'))

def expire_key(key, timeout):
    client = get_client()
    client.expire(key, timeout)
