import redis

from micro_framework.settings import api_settings


def redis_client(host=None, port=None, db=None, password=None):
    """
    Create Client connected to Redis Server
    """
    if not host:
        host = api_settings.REDIS_HOST
    if not port:
        port = api_settings.REDIS_PORT
    if not db:
        db = api_settings.REDIS_DB
    if not password:
        password = api_settings.REDIS_PASSWORD
    return redis.Redis(host=host, port=port, db=db, password=password)
