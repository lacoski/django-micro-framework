from micro_framework.settings import api_settings

def get_real_ip_from_header_meta(request_meta):
    """
    Getting real ip from request meta
    """
    for key_header in api_settings.HEADER_IP_REMOTE:
        real_ip = request_meta.get(key_header, None)
        if real_ip:
            return real_ip

def get_user_agent_from_header_meta(request_meta):
    """
    Getting user agent from request meta
    """
    return request_meta.get('HTTP_USER_AGENT', '')

def check_client_ip_and_token_ip(request):
    """
    Checking client ip with token ip
    """
    if request.auth is None:
        return False

    if getattr(request.auth, 'payload') is None:
        return False

    token_real_ip = request.auth.payload.get(api_settings.USER_IP_CLAIM, '')
    real_ip = get_real_ip_from_header_meta(request.META)
    if token_real_ip != real_ip:
        return False
    return True
