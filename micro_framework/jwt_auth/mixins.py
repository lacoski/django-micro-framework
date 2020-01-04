"""
MIXINS
"""
from django.utils.translation import ugettext_lazy as _

from micro_framework.jwt_auth import acls
from micro_framework.settings import api_settings
from micro_framework.helpers import check_client_ip_and_token_ip

class PermissionRequiredMixin:

    permission = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        ## Checking permission request
        self.check_require_permissions(request)
        self.check_validate_ip_source(request)

    def check_require_permissions(self, request):
        """
        Checking permission
        """
        if self.permission is not None:
            if not acls.action_allowed(request, self.permission):
                self.permission_denied(
                    request, message=_('You do not have permission to perform this action.')
                )

    def check_validate_ip_source(self, request):
        """
        Checking real_ip in request with real_ip in payload token
        """
        if api_settings.VALIDATE_SOURCE_IP and not check_client_ip_and_token_ip(request):
            self.permission_denied(
                request, message=_('Token is invalid.')
            )
