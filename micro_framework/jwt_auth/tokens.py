from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from micro_framework.jwt_auth.exceptions import TokenBackendError, TokenError
from micro_framework.jwt_auth.redis_token.token_manager import \
    RedisRefreshTokenManager, RedisAccessTokenManager
from micro_framework.jwt_auth.utils import (aware_utcnow, datetime_from_epoch,
                                            datetime_to_epoch, format_lazy)
from micro_framework.settings import api_settings


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """
    token_type = None
    lifetime = None

    def __init__(self, token=None, verify=True):
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError(_('Cannot create token with no type or lifetime'))

        self.token = token
        self.current_time = aware_utcnow()

        # Set up token
        if token is not None:
            # An encoded token was provided
            from .state import token_backend

            # Decode token
            try:
                self.payload = token_backend.decode(token, verify=verify)
            except TokenBackendError:
                raise TokenError(_('Token is invalid or expired'))

            if verify:
                self.verify()
        else:
            # New token.  Skip all the verification steps.
            self.payload = {api_settings.TOKEN_TYPE_CLAIM: self.token_type}

            # Set "exp" claim with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)

            # Set "jti" claim
            self.set_jti()

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def __delitem__(self, key):
        del self.payload[key]

    def __contains__(self, key):
        return key in self.payload

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def __str__(self):
        """
        Signs and returns a token as a base64 encoded string.
        """
        from micro_framework.jwt_auth.state import token_backend

        return token_backend.encode(self.payload)

    def verify(self):
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # Ensure token id is present
        if api_settings.JTI_CLAIM not in self.payload:
            raise TokenError(_('Token has no id'))

        self.verify_token_type()

    def verify_token_type(self):
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[api_settings.TOKEN_TYPE_CLAIM]
        except KeyError:
            raise TokenError(_('Token has no type'))

        if self.token_type != token_type:
            raise TokenError(_('Token has wrong type'))

    def set_jti(self):
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self.payload[api_settings.JTI_CLAIM] = uuid4().hex

    def set_exp(self, claim='exp', from_time=None, lifetime=None):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    def check_exp(self, claim='exp', current_time=None):
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime_from_epoch(claim_value)
        if claim_time <= current_time:
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    @classmethod
    def for_user(cls, user, **kwargs):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id
        for key, value in kwargs.items():
            token[key] = value

        return token


class RedisRefreshTokenMixin:
    if 'micro_framework.jwt_auth.redis_token' in settings.INSTALLED_APPS:
        def verify(self, *args, **kwargs):
            self.check_redis_token()
            super().verify(*args, **kwargs)

        def check_redis_token(self):
            jti = self.payload[api_settings.JTI_CLAIM]
            redis_refresh_tokens = RedisRefreshTokenManager()
            try:
                redis_user_token = redis_refresh_tokens.get(jti)
            except Exception as ex:
                raise TokenError(_('Token is invalid'))

        @classmethod
        def for_user(cls, user, **kwargs):
            """
            Adds this token to the redis token list.
            """
            token = super().for_user(user, **kwargs)
            user_id = user.id
            jti = token[api_settings.JTI_CLAIM]
            redis_refresh_tokens = RedisRefreshTokenManager()
            try:
                redis_refresh_tokens.create(token_id=jti, user_id=user_id, payload=token.payload)
            except Exception as ex:
                raise TokenError(_("Something wrong with Token Storage Backend"))
            return token


class RefreshToken(RedisRefreshTokenMixin, Token):
    token_type = 'refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',

        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        'jti',
    )

    @property
    def access_token(self):
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        access = AccessToken()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        if 'micro_framework.jwt_auth.redis_token' in settings.INSTALLED_APPS:
            redis_access_tokens = RedisAccessTokenManager()
            user_id = access[api_settings.USER_ID_CLAIM]
            jti = access[api_settings.JTI_CLAIM]
            redis_access_tokens.create(token_id=jti, user_id=user_id, payload=access.payload)

        return access

class RedisAccessTokenMixin:
    if 'micro_framework.jwt_auth.redis_token' in settings.INSTALLED_APPS:
        def verify(self, *args, **kwargs):
            self.check_redis_token()
            super().verify(*args, **kwargs)

        def check_redis_token(self):
            jti = self.payload[api_settings.JTI_CLAIM]
            redis_access_tokens = RedisAccessTokenManager()
            try:
                redis_access_user_token = redis_access_tokens.get(jti)
            except Exception as ex:
                raise TokenError(_('Token is invalid'))


class AccessToken(RedisAccessTokenMixin, Token):
    token_type = 'access'
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


class UntypedToken(Token):
    token_type = 'untyped'
    lifetime = timedelta(seconds=0)

    def verify_token_type(self):
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        pass


