from django.contrib.auth import get_user_model

from micro_framework.jwt_auth.backends import TokenBackend
from micro_framework.settings import api_settings

User = get_user_model()
token_backend = TokenBackend(api_settings.ALGORITHM, api_settings.SIGNING_KEY,
                             api_settings.VERIFYING_KEY, api_settings.AUDIENCE, api_settings.ISSUER)
