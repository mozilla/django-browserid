# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views.generic.edit import BaseFormView

from django_browserid.forms import BrowserIDForm
from django_browserid.base import get_audience


log = logging.getLogger(__name__)


class Verify(BaseFormView):
    form_class = BrowserIDForm
    failure_url = getattr(settings, 'LOGIN_REDIRECT_URL_FAILURE', '/')
    success_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

    def login_success(self):
        """Handle a successful login. Use this to perform complex redirects
        post-login.
        """
        auth.login(self.request, self.user)
        redirect_field_name = self.kwargs.get('redirect_field_name',
                                              auth.REDIRECT_FIELD_NAME)
        redirect_to = self.request.REQUEST.get(redirect_field_name, None)

        if redirect_to is not None:
            return redirect(redirect_to)
        else:
            return redirect(self.get_success_url())

    def login_failure(self):
        """Handle a failed login. Use this to perform complex redirects
        post-login.
        """
        # Append "?bid_login_failed=1" to the URL to notify the JavaScript that
        # login failed.
        failure_url = self.get_failure_url()

        if not failure_url.endswith('?'):
            failure_url += '?' if not '?' in failure_url else '&'
        failure_url += 'bid_login_failed=1'

        return redirect(failure_url)

    def form_valid(self, form):
        """Handles the return post request from the browserID form and puts
        interesting variables into the class. If everything checks out, then
        we call login_success to decide how to handle a valid user
        """
        self.assertion = form.cleaned_data['assertion']
        self.audience = get_audience(self.request)
        self.user = auth.authenticate(
                assertion=self.assertion,
                audience=self.audience)

        if self.user and self.user.is_active:
            return self.login_success()

        return self.login_failure()

    def form_invalid(self, *args, **kwargs):
        return self.login_failure()

    def get(self, *args, **kwargs):
        return self.login_failure()

    def get_failure_url(self):
        """
        This is just the django version of get_success_url
        https://github.com/django/django/blob/master/django/views/generic/edit.py#L51
        """
        if self.failure_url:
            url = self.failure_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a failure_url.")
        return url

    def dispatch(self, request, *args, **kwargs):
        self.sanity_checks(request)
        return super(Verify, self).dispatch(request, *args, **kwargs)

    def sanity_checks(self, request):
        """Small checks for common errors."""
        if not getattr(settings, 'BROWSERID_ENABLE_SANITY_CHECKS', True):
            return

        # SESSION_COOKIE_SECURE should be False in development unless you can
        # use https.
        if settings.SESSION_COOKIE_SECURE and not request.is_secure():
            log.warning('SESSION_COOKIE_SECURE is currently set to True, which '
                        'may cause issues with django_browserid login during '
                        'local development. Consider setting it to False.')

        # If you're using django-csp, you should include persona.
        if 'csp.middleware.CSPMiddleware' in settings.MIDDLEWARE_CLASSES:
            persona = 'https://login.persona.org'
            in_default = persona in getattr(settings, 'CSP_DEFAULT_SRC', None)
            in_script = persona in getattr(settings, 'CSP_SCRIPT_SRC', None)
            in_frame = persona in getattr(settings, 'CSP_FRAME_SRC', None)

            if (not in_script or not in_frame) and not in_default:
                log.warning('django-csp detected, but {0} was not found in '
                            'your CSP policies. Consider adding it to '
                            'CSP_SCRIPT_SRC and CSP_FRAME_SRC')

