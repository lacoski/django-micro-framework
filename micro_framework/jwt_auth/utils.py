from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.utils.functional import lazy
from django.utils.timezone import is_naive, make_aware, utc

class AclPermission(object):
    def __init__(self, app, action):
        self.app = app
        self.action = action

    @classmethod
    def as_string(cls, string_rule):
        data = str(string_rule).split(":")
        app = data[0]
        action = data[1]
        return cls(app=app, action=action)

    @property
    def string_rule(self):
        return self.app + ':' + self.action

def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)

    return dt


def aware_utcnow():
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return make_utc(datetime.utcfromtimestamp(ts))


def format_lazy(s, *args, **kwargs):
    return s.format(*args, **kwargs)

def roles_to_policies(user):
    list_role = []
    for role_user in user.roles_list:
        service_name, role_name = role_user.split(':')
        if service_name == getattr(settings, 'PORTAL_SERVICE', 'DEFAULT'):
            list_role.append(role_name)
    list_policy = []
    for role_name in list_role:
        try:
            user_policy = Policy.objects.get(name=role_name)
            list_policy.append(user_policy)
        except Exception as ex:
            print('Catch Exception ...')
    return list_policy

format_lazy = lazy(format_lazy, str)
