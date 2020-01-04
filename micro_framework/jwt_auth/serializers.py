from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from micro_framework.helpers import (get_real_ip_from_header_meta,
                                     get_user_agent_from_header_meta)
from micro_framework.jwt_auth.exceptions import InvalidUser
from micro_framework.jwt_auth.state import User
from micro_framework.jwt_auth.tokens import RefreshToken, UntypedToken
from micro_framework.settings import api_settings


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.
        if self.user is None or not self.user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return {}

    @classmethod
    def get_token(cls, user, **kwargs):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user, **kwargs):
        request = kwargs.pop('request')
        if api_settings.ADD_USER_IP_CLAIM:
            kwargs[api_settings.USER_IP_CLAIM] = get_real_ip_from_header_meta(request.META)
        if api_settings.ADD_USER_AGENT_CLAIM:
            kwargs[api_settings.USER_AGENT_CLAIM] = get_user_agent_from_header_meta(request.META)
        return RefreshToken.for_user(user, **kwargs)

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context['request']
        refresh = self.get_token(self.user, request=request)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class VerificationBaseSerializer(serializers.Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_user(self, refresh_token):
        user_id = refresh_token[api_settings.USER_ID_CLAIM]

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            msg = _("User doesn't exist.")
            raise InvalidUser(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise InvalidUser(msg)

        return user

class TokenRefreshSerializer(VerificationBaseSerializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        self._check_user(refresh)

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        UntypedToken(attrs['token'])

        return {}
