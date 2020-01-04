import redis

from micro_framework.settings import api_settings

redis_backend = None
if api_settings.REDIS_ENABLE:
    redis_backend = redis.Redis(host=api_settings.REDIS_HOST,
                                port=api_settings.REDIS_PORT,
                                db=api_settings.REDIS_DB,
                                password=api_settings.REDIS_PASSWORD)
