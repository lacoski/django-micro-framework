from micro_framework.jwt_auth.utils import roles_to_policies

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
