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
    'SERVICE_NAME': 'Demo',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'ISSUER': "TestTest123",
    'SIGNING_KEY': "TestTest123321",
}
```

## Acknowledgments

This project is forked and custom from `https://github.com/davesque/django-rest-framework-simplejwt`