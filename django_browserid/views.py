# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.generic import View

from django_browserid.base import sanity_checks
from django_browserid.http import JSONResponse


logger = logging.getLogger(__name__)


class JSONView(View):
    def http_method_not_allowed(self, *args, **kwargs):
        response = JSONResponse({'error': 'Method not allowed.'}, status=405)
        allowed_methods = [m.upper() for m in self.http_method_names if hasattr(self, m)]
        response['Allow'] = ', '.join(allowed_methods)
        return response


def _get_next(request):
    """
    Get the next parameter from the request's POST arguments and
    validate it.

    :returns:
        The next parameter or None if it was not found or invalid.
    """
    next = request.POST.get('next')
    if is_safe_url(next, host=request.get_host()):
        return next
    else:
        return None


class Verify(JSONView):
    """
    Send an assertion to the remote verification service, and log the
    user in upon success.
    """
    @property
    def failure_url(self):
        """
        URL to redirect users to when login fails. This uses the value
        of ``settings.LOGIN_REDIRECT_URL_FAILURE``, and defaults to
        ``'/'`` if the setting doesn't exist.
        """
        return resolve_url(
            getattr(settings, 'LOGIN_REDIRECT_URL_FAILURE', '/'))

    @property
    def success_url(self):
        """
        URL to redirect users to when login succeeds. This uses the
        value of ``settings.LOGIN_REDIRECT_URL``, and defaults to
        ``'/'`` if the setting doesn't exist.
        """
        return resolve_url(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))

    def login_success(self):
        """Log the user into the site."""
        auth.login(self.request, self.user)

        return JSONResponse({
            'email': self.user.email,
            'redirect': _get_next(self.request) or self.success_url
        })

    def login_failure(self):
        """
        Redirect the user to a login-failed page. By default a 403 is
        returned.
        """
        return JSONResponse({'redirect': self.failure_url}, status=403)

    def post(self, *args, **kwargs):
        """
        Send the given assertion to the remote verification service and,
        depending on the result, trigger login success or failure.
        """
        assertion = self.request.POST.get('assertion')
        if not assertion:
            return self.login_failure()

        self.user = auth.authenticate(request=self.request, assertion=assertion)
        if self.user and self.user.is_active:
            return self.login_success()

        return self.login_failure()

    def dispatch(self, request, *args, **kwargs):
        """
        Run some sanity checks on the request prior to dispatching it.
        """
        sanity_checks(request)
        return super(Verify, self).dispatch(request, *args, **kwargs)


class CsrfToken(JSONView):
    """Fetch a CSRF token for the frontend JavaScript."""
    @never_cache
    def get(self, request):
        # Different CSRF libraries store the CSRF token in different
        # places. Here we support both standard Django CSRF and the
        # django-session-csrf library.
        if hasattr(request, 'csrf_token'):
            csrf_token = request.csrf_token
        else:
            csrf_token = get_token(request)

        return HttpResponse(csrf_token)


class Logout(JSONView):
    @property
    def redirect_url(self):
        """
        URL to redirect users to post-login. Uses
        ``settings.LOGOUT_REDIRECT_URL`` and defaults to ``/`` if the
        setting isn't found.
        """
        return resolve_url(getattr(settings, 'LOGOUT_REDIRECT_URL', '/'))

    def post(self, request):
        """Log the user out."""
        auth.logout(request)

        return JSONResponse({
            'redirect': _get_next(self.request) or self.redirect_url
        })
