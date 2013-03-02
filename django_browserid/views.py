# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
from django.shortcuts import redirect
from django.views.generic.edit import BaseFormView

from django_browserid.base import get_audience, sanity_checks
from django_browserid.forms import BrowserIDForm

# Try to import funfactory's reverse and fall back to django's version.
try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


class Verify(BaseFormView):
    form_class = BrowserIDForm
    failure_url = getattr(settings, 'LOGIN_REDIRECT_URL_FAILURE', '/')
    success_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

    def login_success(self):
        """Handle a successful login. Use this to perform complex redirects
        post-login.
        """
        auth.login(self.request, self.user)
        redirect_to = self.request.REQUEST.get('next', None)

        if redirect_to:
            return redirect(redirect_to)
        else:
            return redirect(self.get_success_url())

    def login_failure(self):
        """Handle a failed login. Use this to perform complex redirects
        post-login.
        """
        failure_url = self.get_failure_url()

        # If this url is a view name, we need to reverse it first to
        # get the url.
        try:
            failure_url = reverse(failure_url)
        except NoReverseMatch:
            pass

        # Append "?bid_login_failed=1" to the URL to notify the
        # JavaScript that the login failed.
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
            raise ImproperlyConfigured('No redirect URL found. Provide a '
                                       'failure_url.')
        return url

    def dispatch(self, request, *args, **kwargs):
        sanity_checks(request)
        return super(Verify, self).dispatch(request, *args, **kwargs)
