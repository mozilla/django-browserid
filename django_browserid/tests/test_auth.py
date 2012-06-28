"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from mock import patch

from django_browserid.auth import BrowserIDBackend, default_username_algo
from django_browserid.tests import mock_browserid


def new_user(email, username=None):
        """Creates a user with the specified email for testing."""
        if username is None:
            username = default_username_algo(email)
        return User.objects.create_user(username, email)


class BrowserIDBackendTests(TestCase):
    def auth(self, verified_email=None):
        """
        Attempt to authenticate a user with BrowserIDBackend.

        If verified_email is None, verification will fail, otherwise it will pass
        and return the specified email.
        """
        with mock_browserid(verified_email):
            backend = BrowserIDBackend()
            return backend.authenticate(assertion='asdf', audience='asdf')

    def test_failed_verification(self):
        """If verification fails, return None."""
        assert self.auth(None) is None

    def test_duplicate_emails(self):
        """If there are two users with the same email address, return None."""
        new_user('a@example.com', 'test1')
        new_user('a@example.com', 'test2')
        assert self.auth('a@example.com') is None

    def test_auth_success(self):
        """
        If a single user is found with the verified email, return an instance of
        their user object.
        """
        user = new_user('a@example.com')
        assert self.auth('a@example.com') == user

    @patch.object(settings, 'BROWSERID_CREATE_USER', False)
    def test_no_create_user(self):
        """If user creation is disabled and no user is found, return None."""
        assert self.auth('a@example.com') is None

    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_create_user(self):
        """
        If user creation is enabled and no user is found, return a new
        User.
        """
        user = self.auth('a@example.com')
        assert user is not None
        assert isinstance(user, User)
        assert user.email == 'a@example.com'

    @patch.object(settings, 'BROWSERID_CREATE_USER',
                  'django_browserid.tests.test_auth.new_user')
    @patch('django_browserid.tests.test_auth.new_user')
    def test_custom_create_user(self, create_user):
        """
        If user creation is enabled with a custom create function and no user
        is found, return the new user created with the custom function.
        """
        create_user.return_value = 'test'
        assert self.auth('a@example.com') == 'test'
        assert create_user.called_with('a@example.com')

    @patch.object(settings, 'BROWSERID_USERNAME_ALGO')
    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_custom_username_algorithm(self, username_algo):
        """If a custom username algorithm is specified, use it!"""
        username_algo.return_value = 'test'
        user = self.auth('a@b.com')
        assert user.username == 'test'

    @patch('django_browserid.signals.user_created')
    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_user_created_signal(self, user_created):
        """
        Test that the user_created signal is called when a new user is created.
        """
        user = self.auth('a@b.com')
        assert user_created.call.called_with(user=user)
