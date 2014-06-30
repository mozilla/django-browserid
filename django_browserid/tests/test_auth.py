# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError

from mock import ANY, Mock, patch

from django_browserid.auth import AutoLoginBackend, BrowserIDBackend, default_username_algo
from django_browserid.base import MockVerifier
from django_browserid.tests import mock_browserid, TestCase

try:
    from django.contrib.auth import get_user_model
    from django_browserid.tests.models import CustomUser
except ImportError:
    get_user_model = False


def new_user(email, username=None):
        """Creates a user with the specified email for testing."""
        if username is None:
            username = default_username_algo(email)
        return User.objects.create_user(username, email)


class BrowserIDBackendTests(TestCase):
    def setUp(self):
        self.backend = BrowserIDBackend()
        self.verifier = Mock()
        self.backend.get_verifier = lambda: self.verifier

    def test_verify_failure(self):
        """If verification fails, return None."""
        self.verifier.verify.return_value = False
        self.assertEqual(self.backend.verify('asdf', 'qwer'), None)
        self.verifier.verify.assert_called_with('asdf', 'qwer')

    def test_verify_success(self):
        """
        If verification succeeds, return the email address from the
        verification result.
        """
        self.verifier.verify.return_value = Mock(email='bob@example.com')
        self.assertEqual(self.backend.verify('asdf', 'qwer'), 'bob@example.com')
        self.verifier.verify.assert_called_with('asdf', 'qwer')

    def test_verify_no_audience_request(self):
        """
        If no audience is provided but a request is, retrieve the
        audience from the request using get_audience.
        """
        request = Mock()
        with patch('django_browserid.auth.get_audience') as get_audience:
            self.backend.verify('asdf', request=request)
            get_audience.assert_called_with(request)
            self.verifier.verify.assert_called_with('asdf', get_audience.return_value)

    def test_verify_no_audience_no_assertion_no_service(self):
        """
        If the assertion isn't provided, or the audience and request
        aren't provided, return None.
        """
        self.assertEqual(self.backend.verify(audience='asdf'), None)
        self.assertEqual(self.backend.verify(assertion='asdf'), None)
        with patch('django_browserid.auth.get_audience') as get_audience:
            get_audience.return_value = None
            self.assertEqual(self.backend.verify('asdf', request=Mock()), None)

    def test_verify_kwargs(self):
        """Any extra kwargs should be passed to the verifier."""
        self.backend.verify('asdf', 'asdf', request='blah', foo='bar', baz=1)
        self.verifier.verify.assert_called_with('asdf', 'asdf', foo='bar', baz=1)

    def auth(self, verified_email=None, **kwargs):
        """
        Attempt to authenticate a user with BrowserIDBackend.

        If verified_email is None, verification will fail, otherwise it will
        pass and return the specified email.
        """
        self.backend.verify = Mock(return_value=verified_email)
        return self.backend.authenticate(assertion='asdf', audience='asdf', **kwargs)

    def test_duplicate_emails(self):
        """
        If there are two users with the same email address, return None.
        """
        new_user('a@example.com', 'test1')
        new_user('a@example.com', 'test2')
        self.assertTrue(self.auth('a@example.com') is None)

    def test_auth_success(self):
        """
        If a single user is found with the verified email, return an
        instance of their user object.
        """
        user = new_user('a@example.com')
        self.assertEqual(self.auth('a@example.com'), user)

    @patch.object(settings, 'BROWSERID_CREATE_USER', False)
    def test_no_create_user(self):
        """
        If user creation is disabled and no user is found, return None.
        """
        self.assertTrue(self.auth('a@example.com') is None)

    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_create_user(self):
        """
        If user creation is enabled and no user is found, return a new
        User.
        """
        user = self.auth('a@example.com')
        self.assertTrue(user is not None)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, 'a@example.com')

    @patch.object(settings, 'BROWSERID_CREATE_USER',
                  'django_browserid.tests.test_auth.new_user')
    @patch('django_browserid.tests.test_auth.new_user')
    def test_custom_create_user(self, create_user):
        """
        If user creation is enabled with a custom create function and no
        user is found, return the new user created with the custom
        function.
        """
        create_user.return_value = 'test'
        self.assertEqual(self.auth('a@example.com'), 'test')
        create_user.assert_called_with('a@example.com')

    @patch.object(settings, 'BROWSERID_USERNAME_ALGO')
    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_custom_username_algorithm(self, username_algo):
        """If a custom username algorithm is specified, use it!"""
        username_algo.return_value = 'test'
        user = self.auth('a@b.com')
        self.assertEqual(user.username, 'test')

    @patch('django_browserid.auth.user_created')
    @patch.object(settings, 'BROWSERID_CREATE_USER', True)
    def test_user_created_signal(self, user_created):
        """
        Test that the user_created signal is called when a new user is
        created.
        """
        user = self.auth('a@b.com')
        user_created.send.assert_called_with(ANY, user=user)

    def test_get_user(self):
        """
        Check if user returned by BrowserIDBackend.get_user is correct.
        """
        user = new_user('a@example.com')
        backend = BrowserIDBackend()
        self.assertEqual(backend.get_user(user.pk), user)

    def test_overriding_valid_email(self):
        class PickyBackend(BrowserIDBackend):
            def is_valid_email(self, email):
                return email != 'a@example.com'

        new_user('a@example.com', 'test1')
        new_user('b@example.com', 'test2')

        with mock_browserid('a@example.com'):
            backend = PickyBackend()
            result = backend.authenticate(assertion='asdf', audience='asdf')
            self.assertTrue(not result)

        with mock_browserid('b@example.com'):
            backend = PickyBackend()
            result = backend.authenticate(assertion='asdf', audience='asdf')
            self.assertTrue(result)

    @patch('django_browserid.auth.logger')
    def test_create_user_integrity_error(self, logger):
        """
        If an IntegrityError is raised during user creation, attempt to
        re-fetch the user in case the user was created since we checked
        for the existing account.
        """
        backend = BrowserIDBackend()
        backend.User = Mock()
        error = IntegrityError()
        backend.User.objects.create_user.side_effect = error
        backend.User.objects.get.return_value = 'asdf'

        self.assertEqual(backend.create_user('a@example.com'), 'asdf')

        # If get raises a DoesNotExist exception, re-raise the original exception.
        backend.User.DoesNotExist = Exception
        backend.User.objects.get.side_effect = backend.User.DoesNotExist
        with self.assertRaises(IntegrityError) as e:
            backend.create_user('a@example.com')
        self.assertEqual(e.exception, error)

    def test_authenticate_verify_exception(self):
        """
        If the verifier raises an exception, log it as a warning and
        return None.
        """
        backend = BrowserIDBackend()
        verifier = Mock()
        exception = Exception()

        backend.get_verifier = lambda: verifier
        verifier.verify.side_effect = exception

        with patch('django_browserid.auth.logger') as logger:
            self.assertEqual(backend.authenticate('asdf', 'asdf'), None)
            logger.warn.assert_called_with(exception)



if get_user_model:
    # Only run custom user model tests if we're using a version of Django that
    # supports it.
    @patch.object(settings, 'AUTH_USER_MODEL', 'tests.CustomUser')
    class CustomUserModelTests(TestCase):
        def _auth(self, backend=None, verified_email=None):
            if backend is None:
                backend = BrowserIDBackend()

            with mock_browserid(verified_email):
                return backend.authenticate(assertion='asdf', audience='asdf')

        def test_existing_user(self):
            """If a custom user exists with the given email, return them."""
            user = CustomUser.objects.create(email='a@test.com')
            authed_user = self._auth(verified_email='a@test.com')
            self.assertEqual(user, authed_user)

        @patch.object(settings, 'BROWSERID_CREATE_USER', True)
        def test_create_new_user(self):
            """
            If a custom user does not exist with the given email, create a new
            user and return them.
            """
            class CustomUserBrowserIDBackend(BrowserIDBackend):
                def create_user(self, email):
                    return CustomUser.objects.create(email=email)
            user = self._auth(backend=CustomUserBrowserIDBackend(),
                              verified_email='b@test.com')
            self.assertTrue(isinstance(user, CustomUser))
            self.assertEqual(user.email, 'b@test.com')


class AutoLoginBackendTests(TestCase):
    def setUp(self):
        self.backend = AutoLoginBackend()

    def test_verify_with_email(self):
        """
        If BROWSERID_AUTOLOGIN_EMAIL is set, use it to auth the user.
        """
        with self.settings(BROWSERID_AUTOLOGIN_EMAIL='bob@example.com',
                           BROWSERID_AUTOLOGIN_ENABLED=True):
            self.assertEqual(self.backend.verify(), 'bob@example.com')

    def test_verify_without_email(self):
        """
        If BROWSERID_AUTOLOGIN_EMAIL is not set, do not auth the user.
        """
        with self.settings(BROWSERID_AUTOLOGIN_EMAIL='', BROWSERID_AUTOLOGIN_ENABLED=True):
            del settings.BROWSERID_AUTOLOGIN_EMAIL
            self.assertEqual(self.backend.verify(), None)

    def test_verify_disabled(self):
        """
        If BROWSERID_AUTOLOGIN_ENABLED is False, do not auth the user
        in any case.
        """
        with self.settings(BROWSERID_AUTOLOGIN_EMAIL='', BROWSERID_AUTOLOGIN_ENABLED=False):
            del settings.BROWSERID_AUTOLOGIN_EMAIL
            self.assertEqual(self.backend.verify(), None)

        with self.settings(BROWSERID_AUTOLOGIN_EMAIL='bob@example.com',
                           BROWSERID_AUTOLOGIN_ENABLED=False):
            self.assertEqual(self.backend.verify(), None)
