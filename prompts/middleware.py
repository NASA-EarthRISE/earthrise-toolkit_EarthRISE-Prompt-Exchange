from django.shortcuts import redirect


# Paths that are always accessible regardless of group membership
_ALLOWED_PREFIXES = (
    '/accounts/',       # allauth login, logout, Google OAuth
    '/admin/',          # Django admin (superusers only, handled by admin itself)
    '/access-denied/',  # access denied page
    '/static/',         # static files
    '/media/',          # media files
)


class EarthRISEAccessMiddleware:
    """
    Restricts access to users in the EarthRISE group.

    - Unauthenticated users are redirected to the login page.
    - Authenticated users not in EarthRISE (and not superuser/staff)
      are redirected to the access-denied page.
    - Superusers and staff bypass the group check.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if any(path.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect('account_login')

        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        if not request.user.groups.filter(name='EarthRISE').exists():
            return redirect('access_denied')

        return self.get_response(request)
