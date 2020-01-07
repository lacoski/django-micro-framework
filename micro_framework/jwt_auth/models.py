# Create your models here.
from django.contrib.auth import models as auth_models
from django.db import models
from django.db.models.manager import EmptyManager
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from micro_framework.jwt_auth.compat import CallableFalse, CallableTrue
from micro_framework.settings import api_settings


class TokenUser:
    """
    A dummy user class modeled after django.contrib.auth.models.AnonymousUser.
    Used in conjunction with the `JWTTokenUserAuthentication` backend to
    implement single sign-on functionality across services which share the same
    secret key.  `JWTTokenUserAuthentication` will return an instance of this
    class instead of a `User` model instance.  Instances of this class act as
    stateless user objects which are backed by validated tokens.
    """
    # User is always active since Simple JWT will never issue a token for an
    # inactive user
    is_active = True
    default_fields = ['username', 'is_staff', 'is_superuser', 'roles',
                      'id', 'pk']

    _groups = EmptyManager(auth_models.Group)
    _user_permissions = EmptyManager(auth_models.Permission)

    def __init__(self, token):
        self.token = token

        for key, value in self.token.payload.items():
            if key not in self.default_fields:
                setattr(self, key, value)

    def __str__(self):
        return 'TokenUser {}'.format(self.id)

    @cached_property
    def id(self):
        return self.token[api_settings.USER_ID_CLAIM]

    @cached_property
    def pk(self):
        return self.id

    @cached_property
    def username(self):
        return self.token.get('username', '')
    
    @cached_property
    def email(self):
        return self.token.get('email', '')

    @cached_property
    def is_staff(self):
        return self.token.get('is_staff', False)

    @cached_property
    def is_superuser(self):
        return self.token.get('is_superuser', False)
    
    @property
    def roles_list(self):
        return self.token.get('roles', [])

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def save(self):
        raise NotImplementedError('Token users have no DB representation')

    def delete(self):
        raise NotImplementedError('Token users have no DB representation')

    def set_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation')

    def check_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation')

    @property
    def groups(self):
        return self._groups

    @property
    def user_permissions(self):
        return self._user_permissions

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        return False

    def has_module_perms(self, module):
        return False

    @property
    def is_anonymous(self):
        return CallableFalse

    @property
    def is_authenticated(self):
        return CallableTrue

    def get_username(self):
        return self.username

class Policy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rules = models.TextField()
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'policies'
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")

    def __str__(self):
        return self.name
