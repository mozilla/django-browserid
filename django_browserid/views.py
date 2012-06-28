"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views.generic.edit import BaseFormView

from django_browserid.forms import BrowserIDForm
from django_browserid.base import get_audience


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
        return redirect(self.get_failure_url())

    def form_valid(self, form):
        """Handles the return post request from the browserID form and puts
        interesting variables into the class. If everything checks out, then
        we call handle_user to decide how to handle a valid user
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
        return redirect(self.get_failure_url())

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
