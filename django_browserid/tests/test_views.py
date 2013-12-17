# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import auth
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from mock import patch

from django_browserid import BrowserIDException, views
from django_browserid.tests import mock_browserid
from django.core.urlresolvers import NoReverseMatch


factory = RequestFactory()


class VerifyTests(TestCase):
    def verify(self, request_type, success_url=None, failure_url=None, **kwargs):
        """
        Call the verify view function. All kwargs not specified above will be passed
        as GET or POST arguments.
        """
        if request_type == 'get':
            request = factory.get('/browserid/verify', kwargs)
        else:
            request = factory.post('/browserid/verify', kwargs)

        # Patch settings prior to importing verify
        patches = {'BROWSERID_CREATE_USER': True, 'SITE_URL': 'http://testserver'}
        if success_url is not None:
            patches['LOGIN_REDIRECT_URL'] = success_url
        if failure_url is not None:
            patches['LOGIN_REDIRECT_URL_FAILURE'] = failure_url

        with self.settings(**patches):
            verify_view = views.Verify.as_view()
            with patch.object(auth, 'login'):
                response = verify_view(request)

        return response

    def test_get_redirect_failure(self):
        # Issuing a GET to the verify view redirects to the failure URL.
        response = self.verify('get', failure_url='/fail')
        assert response.status_code == 302
        assert response['Location'].endswith('/fail?bid_login_failed=1')

    def test_invalid_redirect_failure(self):
        # Invalid form arguments redirect to the failure URL.
        response = self.verify('post', failure_url='/fail', blah='asdf')
        assert response.status_code == 302
        assert response['Location'].endswith('/fail?bid_login_failed=1')

    @mock_browserid(None)
    def test_auth_fail_redirect_failure(self):
        # If authentication fails, redirect to the failure URL.
        response = self.verify('post', failure_url='/fail', assertion='asdf')
        assert response.status_code == 302
        assert response['Location'].endswith('/fail?bid_login_failed=1')

    @mock_browserid(None)
    def test_auth_fail_url_parameters(self):
        # Ensure that bid_login_failed=1 is appended to the failure url.
        response = self.verify('post', failure_url='/fail', assertion='asdf')
        assert response['Location'].endswith('/fail?bid_login_failed=1')

        response = self.verify('post', failure_url='/fail?', assertion='asdf')
        assert response['Location'].endswith('/fail?bid_login_failed=1')

        response = self.verify('post', failure_url='/fail?asdf', assertion='asdf')
        assert response['Location'].endswith('/fail?asdf&bid_login_failed=1')

        response = self.verify('post', failure_url='/fail?asdf=4', assertion='asdf')
        assert response['Location'].endswith('/fail?asdf=4&bid_login_failed=1')

        response = self.verify('post', failure_url='/fail?asdf=4&bid_login_failed=1',
                          assertion='asdf')
        assert response['Location'].endswith('/fail?asdf=4&bid_login_failed=1'
                                             '&bid_login_failed=1')

    @mock_browserid(None)
    @patch('django_browserid.views.logger.error')
    @patch('django_browserid.views.auth.authenticate')
    def test_authenticate_browserid_exception(self, authenticate, logger_error):
        # If authenticate raises a BrowserIDException, redirect to the failure URL.
        excpt = BrowserIDException(Exception('hsakjw'))
        authenticate.side_effect = excpt

        response = self.verify('post', failure_url='/fail', assertion='asdf')
        assert response.status_code == 302
        assert response['Location'].endswith('/fail?bid_login_failed=1')
        logger_error.assert_called_with(excpt)

    @mock_browserid('test@example.com')
    def test_auth_success_redirect_success(self):
        # If authentication succeeds, redirect to the success URL.
        response = self.verify('post', success_url='/success', assertion='asdf')
        assert response.status_code == 302
        assert response['Location'].endswith('/success')

    @mock_browserid('test@example.com')
    def test_redirect_field(self):
        # If a redirect is passed as an argument to the request, redirect to that
        # instead of the success URL.
        kwargs = {'next': '/field_success', 'assertion': 'asdf'}
        response = self.verify('post', success_url='/success', **kwargs)
        assert response.status_code == 302
        assert response['Location'].endswith('/field_success')

    @mock_browserid('test@example.com')
    def test_redirect_invalid_host(self):
        # If the given redirect url points to an invalid host, redirect to the
        # default failure URL.
        response = self.verify('post', next='http://example.com/login_failure',
                          success_url='/woo', assertion='asdf')
        assert response.status_code == 302
        assert response['Location'].endswith('/woo')

    @override_settings(DEBUG=True, SESSION_COOKIE_SECURE=True)
    @patch('django_browserid.views.logger.debug')
    @mock_browserid(None)
    def test_sanity_session_cookie(self, debug):
        # If DEBUG == True and SESSION_COOKIE_SECURE == True, log a debug message
        # warning about it.
        self.verify('post', assertion='asdf')
        debug.called = True

    @override_settings(DEBUG=True, MIDDLEWARE_CLASSES=['csp.middleware.CSPMiddleware'])
    @patch('django_browserid.views.logger.debug')
    @mock_browserid(None)
    def test_sanity_csp(self, debug):
        # If DEBUG == True, the django-csp middleware is present, and Persona isn't
        # allowed by CSP, log a debug message warning about it.

        # Test if allowed properly.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=['https://login.persona.org'],
                           CSP_FRAME_SRC=['https://login.persona.org']):
            self.verify('post', assertion='asdf')
            debug.called = False
        debug.reset_mock()

        # Test fallback to default-src.
        with self.settings(CSP_DEFAULT_SRC=['https://login.persona.org'],
                           CSP_SCRIPT_SRC=[],
                           CSP_FRAME_SRC=[]):
            self.verify('post', assertion='asdf')
            debug.called = False
        debug.reset_mock()

        # Test incorrect csp.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=[],
                           CSP_FRAME_SRC=[]):
            self.verify('post', assertion='asdf')
            debug.called = True
        debug.reset_mock()

        # Test partial incorrectness.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=['https://login.persona.org'],
                           CSP_FRAME_SRC=[]):
            self.verify('post', assertion='asdf')
            debug.called = True    

    @patch('django_browserid.views.reverse')
    def test_reverse_redirect(self, reverse):
        view = views.Verify()
        with self.settings(LOGIN_REDIRECT_URL='main:home'):            
            assert view.success_url == reverse('main:home')

