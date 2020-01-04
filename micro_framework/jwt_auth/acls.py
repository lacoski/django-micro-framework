from django.utils.translation import ugettext_lazy as _

from micro_framework.jwt_auth.exceptions import InvalidToken
from micro_framework.jwt_auth.models import Policy
from micro_framework.settings import api_settings


def match_rules(rules, app, action):
    """
    This will match rules found in Policy.
    """
    for rule in rules.split(','):
        try:
            rule_app, rule_action = rule.split(':')

            # Loại bỏ dấu cách nếu thừa
            rule_app = rule_app.replace(" ", "")
            rule_action = rule_action.replace(" ", "")

            if rule_app == '*' or rule_app == app:
                if rule_action == '*' or rule_action == action or action == '%':
                    return True
        except Exception as ex:
            continue
    return False

def action_allowed(request, permission):
    return action_allowed_user(request.user, permission)

def action_allowed_user(user, permission):
    if not user.is_authenticated:
        return False

    return any(
        match_rules(policy.rules, permission.app, permission.action)
        for policy in roles_to_policies(user)
    )

def roles_to_policies(user):
    list_role = []
    for role_user in user.roles_list:
        service_name, role_name = role_user.split(':')
        if service_name == api_settings.SERVICE_NAME:
            list_role.append(role_name)
    list_policy = []
    for role_name in list_role:
        try:
            user_policy = Policy.objects.get(name=role_name)
            list_policy.append(user_policy)
        except Exception as ex:
            messages = []
            messages.append({'message': str(ex)})
            raise InvalidToken({
                'detail': _('Given token not valid for any token type'),
                'messages': messages,
            })
    return list_policy
