"""
MIXINS
"""

class PermissionRequiredMixin:

    permission = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        ## Check request có đủ quyền xử lý
        self.check_require_permissions(request)

    def check_require_permissions(self, request):
        """
        Checking permission
        """
        if self.permission is not None:
            from core.jwt_acl import acls
            if not acls.action_allowed(request, self.permission):
                self.permission_denied(
                    request, message='Bạn không có quyền thực hiện thao tác này'
                )
