from django.core.management.base import BaseCommand, CommandError

from micro_framework.jwt_auth.redis_token.token_manager import RedisAccessTokenManager


class Command(BaseCommand):
    help = 'Revoke token store in Redis'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--all', action='store_true', help='Revoke all token storing in redis')
        parser.add_argument('-uid', '--user_id', type=str, help='Revoke all token belong to user_id')

    def handle(self, *args, **kwargs):
        redis_access_tokens = RedisAccessTokenManager()
        all = kwargs['all']
        if all:
            redis_access_tokens.delete_all()
            print("All access token has been revoke")

        user_id = kwargs.get('user_id', None)
        if user_id:
            list_user_token = redis_access_tokens.list(user_id=user_id)
            for redis_token in list_user_token:
                redis_token.delete()
            msg = "All access token belong to {} has been revoke".format(user_id)
            print(msg)
