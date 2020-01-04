from django.utils.functional import cached_property

from micro_framework.settings import api_settings
from micro_framework.store.redis_backend.client import redis_client
from micro_framework.store.redis_backend.utils import data_to_json, redis_to_data

# Cấu trúc tokens:<token_id>:<user_id>
TOKEN_KEY = "tokens:{}:{}"

def get_token_key(token_id, user_id):
    return TOKEN_KEY.format(token_id, user_id)

class RedisTokenManager:
    """
    Redis Token Manager
    """
    def create(self, token_id, user_id, payload):
        redis_backend = redis_client()
        redis_token_key = get_token_key(token_id, user_id)
        redis_timeout = None
        if api_settings.REDIS_EXPIRE_TOKEN:
            redis_timeout = int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds())
        redis_backend.set(
            redis_token_key,
            data_to_json(payload),
            ex=redis_timeout
        )
        return self.get(token_id)

    def list(self, user_id=None):
        redis_backend = redis_client()
        if not user_id:
            user_id = '*'
        list_token_by_user_id = redis_backend.keys(get_token_key('*', user_id))
        list_redis_token = []
        for redis_token_key in list_token_by_user_id:
            redis_token = RedisToken(redis_token_key, redis_backend.get(redis_token_key))
            list_redis_token.append(redis_token)
        return list_redis_token

    def get(self, token_id):
        redis_backend = redis_client()
        list_token_by_token_id = redis_backend.keys(get_token_key(token_id, '*'))
        if len(list_token_by_token_id) < 1:
            raise ValueError("Token does not exist")
        return RedisToken(list_token_by_token_id[0], redis_backend.get(list_token_by_token_id[0]))

    def delete(self, token_id):
        redis_backend = redis_client()
        list_token_by_token_id = redis_backend.keys(get_token_key(token_id, '*'))
        return redis_backend.delete(*list_token_by_token_id)

    def delete_all(self):
        redis_backend = redis_client()
        list_token_by_token_id = redis_backend.keys(get_token_key('*', '*'))
        if len(list_token_by_token_id) > 0:
            return redis_backend.delete(*list_token_by_token_id)
        return 0

class RedisToken:
    """
    Redis Token
    """
    def __init__(self, redis_key, payload):
        if isinstance(redis_key, bytes):
            redis_key = redis_key.decode("utf8")
        if isinstance(payload, bytes):
            payload = redis_to_data(payload)

        self.redis_key = redis_key
        self.payload = payload

    def __repr__(self):
        return "<RedisToken: %s>" % (self.redis_key or 'unknown')

    def __iter__(self):
        yield self.token_id, self.payload


    @cached_property
    def redis_backend(self):
        return redis_client()

    @property
    def token_id(self):
        return self.redis_key.split(':')[1]

    @property
    def user_id(self):
        return self.payload.get(api_settings.USER_ID_CLAIM, None)

    @property
    def time_to_live(self):
        return self.redis_backend.ttl(self.redis_key)

    def delete(self):
        return self.redis_backend.delete(self.redis_key)
