# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import auth
from django.test.client import RequestFactory

from mock import patch
from nose.tools import eq_, ok_

from django_browserid import BrowserIDException, views
from django_browserid.tests import mock_browserid, TestCase


class JSONViewTests(TestCase):
    def test_http_method_not_allowed(self):
        class TestView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'
        response = TestView().http_method_not_allowed()
        eq_(response.status_code, 405)
        ok_(set(['GET']).issubset(set(response['Allow'].split(', '))))
        self.assert_json_equals(response.content, {'error': 'Method not allowed.'})

    def test_http_method_not_allowed_allowed_methods(self):
        class GetPostView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'

            def post(self, request, *args, **kwargs):
                return 'qwer'
        response = GetPostView().http_method_not_allowed()
        ok_(set(['GET', 'POST']).issubset(set(response['Allow'].split(', '))))

        class GetPostPutDeleteHeadView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'

            def post(self, request, *args, **kwargs):
                return 'qwer'

            def put(self, request, *args, **kwargs):
                return 'qwer'

            def delete(self, request, *args, **kwargs):
                return 'qwer'

            def head(self, request, *args, **kwargs):
                return 'qwer'
        response = GetPostPutDeleteHeadView().http_method_not_allowed()
        expected_methods = set(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
        actual_methods = set(response['Allow'].split(', '))
        ok_(expected_methods.issubset(actual_methods))


class VerifyTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def verify(self, request_type, **kwargs):
        """
        Call the verify view function. Kwargs are passed as GET or POST
        arguments.
        """
        if request_type == 'get':
            request = self.factory.get('/browserid/verify', kwargs)
        else:
            request = self.factory.post('/browserid/verify', kwargs)

        verify_view = views.Verify.as_view()
        with patch.object(auth, 'login'):
            response = verify_view(request)

        return response

    def test_no_assertion(self):
        """If no assertion is given, return a failure result."""
        with self.settings(LOGIN_REDIRECT_URL_FAILURE='/fail'):
            response = self.verify('post', blah='asdf')
        eq_(response.status_code, 403)
        self.assert_json_equals(response.content, {'redirect': '/fail'})

    @mock_browserid(None)
    def test_auth_fail(self):
        """If authentication fails, redirect to the failure URL."""
        with self.settings(LOGIN_REDIRECT_URL_FAILURE='/fail'):
            response = self.verify('post', assertion='asdf')
        eq_(response.status_code, 403)
        self.assert_json_equals(response.content, {'redirect': '/fail'})

    @mock_browserid(None)
    @patch('django_browserid.views.logger.error')
    @patch('django_browserid.views.auth.authenticate')
    def test_authenticate_browserid_exception(self, authenticate, logger_error):
        """
        If authenticate raises a BrowserIDException, return a failure
        response.
        """
        excpt = BrowserIDException(Exception('hsakjw'))
        authenticate.side_effect = excpt

        with patch.object(views.Verify, 'login_failure') as mock_failure:
            response = self.verify('post', assertion='asdf')
        eq_(response, mock_failure.return_value)
        mock_failure.assert_called_with(excpt)

    def test_login_failure_log_exception(self):
        """If login_failure is passed an exception, it should log it."""
        excpt = BrowserIDException(Exception('hsakjw'))

        with patch('django_browserid.views.logger.error') as logger_error:
            views.Verify().login_failure(excpt)
        logger_error.assert_called_with(excpt)

    @mock_browserid('test@example.com')
    def test_auth_success_redirect_success(self):
        """If authentication succeeds, redirect to the success URL."""
        user = auth.models.User.objects.create_user('asdf', 'test@example.com')

        request = self.factory.post('/browserid/verify', {'assertion': 'asdf'})
        with self.settings(LOGIN_REDIRECT_URL='/success'):
            with patch('django_browserid.views.auth.login') as login:
                verify = views.Verify.as_view()
                response = verify(request)

        login.assert_called_with(request, user)
        eq_(response.status_code, 200)
        self.assert_json_equals(response.content,
                                {'email': 'test@example.com', 'redirect': '/success'})

    def test_sanity_checks(self):
        """Run sanity checks on all incoming requests."""
        with patch('django_browserid.views.sanity_checks') as sanity_checks:
            self.verify('post')
        ok_(sanity_checks.called)


class LogoutTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_redirect(self):
        """Include LOGOUT_REDIRECT_URL in the response."""
        request = self.factory.post('/')
        logout = views.Logout.as_view()

        with self.settings(LOGOUT_REDIRECT_URL='/test/foo'):
            with patch('django_browserid.views.auth.logout') as auth_logout:
                response = logout(request)

        auth_logout.assert_called_with(request)
        eq_(response.status_code, 200)
        self.assert_json_equals(response.content, {'redirect': '/test/foo'})
