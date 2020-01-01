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

    def test_credentials_wrong(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': 'test_user',
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('detail', res.data)

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('detail', res.data)

    def test_success(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)


class TestTokenRefreshView(APIViewTestCase):
    view_name = 'token_refresh'

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
        self.assertIn('refresh', res.data)

    def test_it_should_return_401_if_token_invalid(self):
        token = RefreshToken()
        del token['exp']

        res = self.view_post(data={'refresh': str(token)})
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data['code'], 'token_not_valid')

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(data={'refresh': str(token)})
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data['code'], 'token_not_valid')

    def test_it_should_return_access_token_if_everything_ok(self):
        refresh = RefreshToken()
        refresh['test_claim'] = 'arst'

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch('micro_framework.tokens.aware_utcnow') as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now

            res = self.view_post(data={'refresh': str(refresh)})

        self.assertEqual(res.status_code, 200)

        access = AccessToken(res.data['access'])

        self.assertEqual(refresh['test_claim'], access['test_claim'])
        self.assertEqual(access['exp'], datetime_to_epoch(now + api_settings.ACCESS_TOKEN_LIFETIME))


class TestTokenObtainSlidingView(APIViewTestCase):
    view_name = 'token_obtain_sliding'

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

    def test_credentials_wrong(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': 'test_user',
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('detail', res.data)

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('detail', res.data)

    def test_success(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.data)


class TestTokenRefreshSlidingView(APIViewTestCase):
    view_name = 'token_refresh_sliding'

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
        self.assertIn('token', res.data)


class TestTokenVerifyView(APIViewTestCase):
    view_name = 'token_verify'

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
        self.assertIn('token', res.data)

    def test_it_should_return_200_if_everything_okay(self):
        token = RefreshToken()

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_it_should_ignore_token_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = 'fake_type'

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)
