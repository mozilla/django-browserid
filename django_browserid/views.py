import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import BaseFormView

from django_browserid.forms import BrowserIDForm
from django_browserid.base import get_audience


class Verify(BaseFormView):
    form_class = BrowserIDForm
    failure_url = getattr(settings, 'LOGIN_REDIRECT_URL_FAILURE', '/')
    success_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

    def handle_user(self, request, user):
        """
        This view takes an authenticated user and logs them in. This view
        should be subclassed to accomplish more complicated behavior
        """
        auth.login(request, user)
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        """
        Handles the return post request from the browserID form and puts
        interesting variables into the class. If everything checks out, then
        we call handle_user to decide how to handle a valid user
        """
        self.assertion = form.cleaned_data['assertion']
        self.audience = get_audience(self.request)
        self.user = auth.authenticate(
                assertion=self.assertion,
                audience=self.audience)

        if self.user and self.user.is_active:
            return self.handle_user(self.request, self.user)

        return HttpResponseRedirect(self.get_failure_url())

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

    def get(self, *args, **kwargs):
        return redirect('/')

    def form_invalid(self, *args, **kwargs):
        return redirect(self.get_failure_url())
