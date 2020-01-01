from datetime import timedelta
from unittest.mock import patch

from micro_framework.jwt_auth.settings import api_settings
from micro_framework.jwt_auth.state import User
from micro_framework.jwt_auth.tokens import AccessToken, RefreshToken
from micro_framework.jwt_auth.utils import (aware_utcnow, datetime_from_epoch,
                                            datetime_to_epoch)

from tests.utils import APIViewTestCase


class TestTokenObtainPairView(APIViewTestCase):
    view_name = 'token_obtain_pair'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={})
        self.assertEqual(res.status_code, 400)
        self.assertIn(User.USERNAME_FIELD, res.data)
        self.assertIn('password', res.data)

        res = self.view_post(data={User.USERNAME_FIELD: self.username})
        self.assertEqual(res.status_code, 400)
        self.assertIn('password', res.data)

        res = self.view_post(data={'password': self.password})
        self.assertEqual(res.status_code, 400)
        self.assertIn(User.USERNAME_FIELD, res.data)
