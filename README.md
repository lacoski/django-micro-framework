# Django Micro framework
> Micro framework for Django REST Framework

---
## Requirements
- Python (3.6)
- Django (2.0, 2.1, 2.2, 3.0)
- Django REST Framework (3.8, 3.9, 3.10)

## Installation
Micro Framework can be installed with pip
```
pip install djangomicroframework
```

Then, go to your django project. In `settings.py`:
```
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'micro_framework.jwt_auth.authentication.JWTTokenUserAuthentication',
    ]
}

from datetime import timedelta
MICRO_FRAMEWORK = {
    'SERVICE_NAME': 'Default',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('micro_framework.jwt_auth.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    # Custom payload Token
    'ADD_USER_IP_CLAIM': False,
    'USER_IP_CLAIM': 'user_ip',

    'ADD_USER_AGENT_CLAIM': False,
    'USER_AGENT_CLAIM': 'user_agent',

    'VALIDATE_SOURCE_IP': False,
    'HEADER_IP_REMOTE': ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'],
    

    # Redis backend
    'REDIS_ENABLE': False,
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': 6379,
    'REDIS_PASSWORD': None,
    'REDIS_DB': 0,
    'REDIS_EXPIRE_TOKEN': False,
}
```

## Acknowledgments

This project is forked and custom from `https://github.com/davesque/django-rest-framework-simplejwt`