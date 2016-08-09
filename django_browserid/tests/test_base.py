# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime
from itertools import cycle

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.utils import six
from django.utils.functional import lazy

import requests
from mock import Mock, patch

from django_browserid import base
from django_browserid.compat import pybrowserid_found
from django_browserid.tests import TestCase


class SanityCheckTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(DEBUG=True)
    def test_debug_true(self):
        """
        If DEBUG is True and BROWSERID_DISABLE_SANITY_CHECKS is not set,
        run the checks.
        """
        request = self.factory.get('/')
        self.assertTrue(base.sanity_checks(request))

    @override_settings(DEBUG=False)
    def test_debug_false(self):
        """
        If DEBUG is True and BROWSERID_DISABLE_SANITY_CHECKS is not set,
        run the checks.
        """
        request = self.factory.get('/')
        self.assertTrue(not base.sanity_checks(request))

    @override_settings(BROWSERID_DISABLE_SANITY_CHECKS=True)
    def test_disable_sanity_checks(self):
        """
        If BROWSERID_DISABLE_SANITY_CHECKS is True, do not run any
        checks.
        """
        request = self.factory.get('/')
        self.assertTrue(not base.sanity_checks(request))

    @override_settings(BROWSERID_DISABLE_SANITY_CHECKS=False, SESSION_COOKIE_SECURE=True)
    def test_sanity_session_cookie(self):
        """
        If SESSION_COOKIE_SECURE == True and the current request isn't
        https, log a debug message warning about it.
        """
        request = self.factory.get('/')
        request.is_secure = Mock(return_value=False)
        with patch('django_browserid.base.logger.warning') as warning:
            base.sanity_checks(request)
        self.assertTrue(warning.called)

    @override_settings(BROWSERID_DISABLE_SANITY_CHECKS=False,
                       MIDDLEWARE_CLASSES=['csp.middleware.CSPMiddleware'])
    @patch('django_browserid.base.logger.warning')
    def test_sanity_csp(self, warning):
        """
        If the django-csp middleware is present and Persona isn't
        allowed by CSP, log a debug message warning about it.
        """
        request = self.factory.get('/')

        # Test if allowed properly.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=['https://login.persona.org'],
                           CSP_FRAME_SRC=['https://login.persona.org']):
            base.sanity_checks(request)
        self.assertTrue(not warning.called)
        warning.reset_mock()

        # Test fallback to default-src.
        with self.settings(CSP_DEFAULT_SRC=['https://login.persona.org'],
                           CSP_SCRIPT_SRC=[],
                           CSP_FRAME_SRC=[]):
            base.sanity_checks(request)
        self.assertTrue(not warning.called)
        warning.reset_mock()

        # Test incorrect csp.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=[],
                           CSP_FRAME_SRC=[]):
            base.sanity_checks(request)
        self.assertTrue(warning.called)
        warning.reset_mock()

        # Test partial incorrectness.
        with self.settings(CSP_DEFAULT_SRC=[],
                           CSP_SCRIPT_SRC=['https://login.persona.org'],
                           CSP_FRAME_SRC=[]):
            base.sanity_checks(request)
        self.assertTrue(warning.called)

    @override_settings(BROWSERID_DISABLE_SANITY_CHECKS=False,
                       MIDDLEWARE_CLASSES=['csp.middleware.CSPMiddleware'])
    @patch('django_browserid.base.logger.warning')
    def test_unset_csp(self, warning):
        """Check for errors when CSP settings aren't specified."""
        request = self.factory.get('/')
        correct = ['https://login.persona.org']
        setting_kwargs = {
            'CSP_DEFAULT_SRC': correct,
            'CSP_SCRIPT_SRC': correct,
            'CSP_FRAME_SRC': correct
        }

        # There's no easy way to use a variable for deleting the
        # attribute on the settings object, so we can't easily turn this
        # into a function, sadly.
        with self.settings(**setting_kwargs):
            del settings.CSP_DEFAULT_SRC
            base.sanity_checks(request)
        self.assertTrue(not warning.called)
        warning.reset_mock()

        with self.settings(**setting_kwargs):
            del settings.CSP_FRAME_SRC
            base.sanity_checks(request)
        self.assertTrue(not warning.called)
        warning.reset_mock()

        with self.settings(**setting_kwargs):
            del settings.CSP_SCRIPT_SRC
            base.sanity_checks(request)
        self.assertTrue(not warning.called)
        warning.reset_mock()


class GetAudienceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_setting_missing(self):
        """
        If BROWSERID_AUDIENCES isn't defined, raise
        ImproperlyConfigured.
        """
        request = self.factory.get('/')

        with patch('django_browserid.base.settings') as settings:
            del settings.BROWSERID_AUDIENCES
            settings.DEBUG = False

            with self.assertRaises(ImproperlyConfigured):
                base.get_audience(request)

    def test_same_origin_found(self):
        """
        If an audience is found in BROWSERID_AUDIENCES with the same
        origin as the request URI, return it.
        """
        request = self.factory.get('http://testserver')

        audiences = ['https://example.com', 'http://testserver']
        with self.settings(BROWSERID_AUDIENCES=audiences, DEBUG=False):
            self.assertEqual(base.get_audience(request), 'http://testserver')

    def test_no_audience(self):
        """
        If no matching audiences is found in BROWSERID_AUDIENCES, raise
        ImproperlyConfigured.
        """
        request = self.factory.get('http://testserver')

        with self.settings(BROWSERID_AUDIENCES=['https://example.com']):
            with self.assertRaises(ImproperlyConfigured):
                base.get_audience(request)

    def test_missing_setting_but_in_debug(self):
        """
        If no BROWSERID_AUDIENCES is set but in DEBUG just use the
        current protocal and host.
        """
        request = self.factory.get('/')

        # Simulate that no BROWSERID_AUDIENCES has been set
        with patch('django_browserid.base.settings') as settings:
            del settings.BROWSERID_AUDIENCES
            settings.DEBUG = True
            self.assertEqual(base.get_audience(request), 'http://testserver')

    def test_no_audience_but_in_debug(self):
        """
        If no BROWSERID_AUDIENCES is set but in DEBUG just use the
        current protocal and host.
        """
        request = self.factory.get('/')

        # Simulate that no BROWSERID_AUDIENCES has been set
        with self.settings(BROWSERID_AUDIENCES=[], DEBUG=True):
            self.assertEqual(base.get_audience(request), 'http://testserver')


class VerificationResultTests(TestCase):
    def test_getattr_attribute_exists(self):
        """
        If a value exists in the response dict, it should be an
        attribute on the result.
        """
        result = base.VerificationResult({'myattr': 'foo'})
        self.assertEqual(result.myattr, 'foo')

    def test_getattr_attribute_doesnt_exist(self):
        """
        If a value doesn't exist in the response dict, accessing it as
        an attribute should raise an AttributeError.
        """
        result = base.VerificationResult({'myattr': 'foo'})
        with self.assertRaises(AttributeError):
            result.bar

    def test_expires_no_attribute(self):
        """
        If no expires attribute was in the response, raise an
        AttributeError.
        """
        result = base.VerificationResult({'myattr': 'foo'})
        with self.assertRaises(AttributeError):
            result.expires

    def test_expires_invalid_timestamp(self):
        """
        If the expires attribute cannot be parsed as a timestamp, return
        the raw string instead.
        """
        result = base.VerificationResult({'expires': 'foasdfhas'})
        self.assertEqual(result.expires, 'foasdfhas')

    def test_expires_valid_timestamp(self):
        """
        If expires contains a valid millisecond timestamp, return a
        corresponding datetime.
        """
        result = base.VerificationResult({'expires': '1379307128000'})
        self.assertEqual(datetime(2013, 9, 16, 4, 52, 8), result.expires)

    def test_nonzero_failure(self):
        """
        If the response status is not 'okay', the result should be
        falsy.
        """
        self.assertTrue(not base.VerificationResult({'status': 'failure'}))

    def test_nonzero_okay(self):
        """
        If the response status is 'okay', the result should be truthy.
        """
        self.assertTrue(base.VerificationResult({'status': 'okay'}))

    def test_str_success(self):
        """
        If the result is successful, include 'Success' and the email in
        the string.
        """
        result = base.VerificationResult({'status': 'okay', 'email': 'a@example.com'})
        self.assertEqual(six.text_type(result), '<VerificationResult Success email=a@example.com>')

        # If the email is missing, don't include it.
        result = base.VerificationResult({'status': 'okay'})
        self.assertEqual(six.text_type(result), '<VerificationResult Success>')

    def test_str_failure(self):
        """
        If the result is a failure, include 'Failure' in the string.
        """
        result = base.VerificationResult({'status': 'failure'})
        self.assertEqual(six.text_type(result), '<VerificationResult Failure>')

    def test_str_unicode(self):
        """Ensure that __str__ can handle unicode values."""
        result = base.VerificationResult({'status': 'okay', 'email': six.u('\x80@example.com')})
        self.assertEqual(six.text_type(result), six.u('<VerificationResult Success email=\x80@example.com>'))


class RemoteVerifierTests(TestCase):
    def _response(self, **kwargs):
        return Mock(spec=requests.Response, **kwargs)

    def test_verify_requests_parameters(self):
        """
        If a subclass overrides requests_parameters, the parameters
        should be passed to requests.post.
        """
        class MyVerifier(base.RemoteVerifier):
            requests_parameters = {'foo': 'bar'}
        verifier = MyVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{"status":"failure"}')
            verifier.verify('asdf', 'http://testserver')

        # foo parameter passed with 'bar' value.
        self.assertEqual(post.call_args[1]['foo'], 'bar')

    def test_verify_kwargs(self):
        """
        Any keyword arguments passed to verify should be passed on as
        POST arguments.
        """
        verifier = base.RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{"status":"failure"}')
            verifier.verify('asdf', 'http://testserver', foo='bar', baz=5)

        # foo parameter passed with 'bar' value.
        self.assertEqual(post.call_args[1]['data']['foo'], 'bar')
        self.assertEqual(post.call_args[1]['data']['baz'], 5)

    def test_verify_request_exception(self):
        """
        If a RequestException is raised during the POST, raise a
        BrowserIDException with the RequestException as the cause.
        """
        verifier = base.RemoteVerifier()
        request_exception = requests.exceptions.RequestException()

        with patch('django_browserid.base.requests.post') as post:
            post.side_effect = request_exception
            with self.assertRaises(base.BrowserIDException) as cm:
                verifier.verify('asdf', 'http://testserver')

        self.assertEqual(cm.exception.exc, request_exception)

    def test_verify_lazy_audiences(self):
        """
        If audience is a lazily evaluated object, it should be
        materialized during verification.
        """
        verifier = base.RemoteVerifier()
        audiences = cycle(['http://url1', 'http://url2'])
        audience = lazy(lambda: next(audiences), str)()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{"status":"failure"}')

            verifier.verify('asdf', audience, foo='bar', baz=5)
            self.assertEqual(post.call_args[1]['data']['audience'], 'http://url1')
            post.mock_reset()

            verifier.verify('asdf', audience, foo='bar', baz=5)
            self.assertEqual(post.call_args[1]['data']['audience'], 'http://url2')

    def test_verify_invalid_json(self):
        """
        If the response contains invalid JSON, return a failure result.
        """
        verifier = base.RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            response = self._response(content='{asg9=3{{{}}{')
            response.json.side_effect = ValueError("Couldn't parse json")
            post.return_value = response
            result = verifier.verify('asdf', 'http://testserver')
        self.assertTrue(not result)
        self.assertTrue(result.reason.startswith('Could not parse verifier response'))

    def test_verify_success(self):
        """
        If the response contains valid JSON, return a result object for
        that response.
        """
        verifier = base.RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            response = self._response(
                content='{"status": "okay", "email": "foo@example.com"}')
            response.json.return_value = {"status": "okay", "email": "foo@example.com"}
            post.return_value = response
            result = verifier.verify('asdf', 'http://testserver')
        self.assertTrue(result)
        self.assertEqual(result.email, 'foo@example.com')


class MockVerifierTests(TestCase):
    def test_verify_no_email(self):
        """
        If the given email is None, verify should return a failure
        result.
        """
        verifier = base.MockVerifier(None)
        result = verifier.verify('asdf', 'http://testserver')
        self.assertTrue(not result)
        self.assertEqual(result.reason, 'No email given to MockVerifier.')

    def test_verify_email(self):
        """
        If an email is given to the constructor, return a successful
        result.
        """
        verifier = base.MockVerifier('a@example.com')
        result = verifier.verify('asdf', 'http://testserver')
        self.assertTrue(result)
        self.assertEqual(result.audience, 'http://testserver')
        self.assertEqual(result.email, 'a@example.com')

    def test_verify_result_attributes(self):
        """Extra kwargs to the constructor are added to the result."""
        verifier = base.MockVerifier('a@example.com', foo='bar', baz=5)
        result = verifier.verify('asdf', 'http://testserver')
        self.assertEqual(result.foo, 'bar')
        self.assertEqual(result.baz, 5)

    def test_verify_lazy_audiences(self):
        """
        If audience is a lazily evaluated object, it should be
        materialized during verification.
        """
        verifier = base.MockVerifier('asdf')
        audiences = cycle(['http://url1', 'http://url2'])
        audience = lazy(lambda: next(audiences), str)()

        self.assertEqual(verifier.verify('asdf', audience).audience, 'http://url1')
        self.assertEqual(verifier.verify('asdf', audience).audience, 'http://url2')


class LocalVerifierTests(TestCase):
    def setUp(self):
        # Skip tests if PyBrowserID is not installed.
        if not pybrowserid_found:
            self.skipTest('PyBrowserID required for test but not installed.')

        self.verifier = base.LocalVerifier()

    def test_verify_error(self):
        """
        If verify raises a PyBrowserIDError, return a failure
        result.
        """
        from browserid.errors import Error as PyBrowserIDError

        pybid_verifier = Mock()
        error = PyBrowserIDError()
        self.verifier.pybid_verifier = pybid_verifier

        pybid_verifier.verify.side_effect = error

        result = self.verifier.verify('asdf', 'qwer')
        pybid_verifier.verify.assert_called_with('asdf', 'qwer')
        self.assertFalse(result)
        self.assertEqual(result.reason, error)

    def test_verify_success(self):
        pybid_verifier = Mock()
        self.verifier.pybid_verifier = pybid_verifier

        response = {'status': 'okay'}
        pybid_verifier.verify.return_value = response

        result = self.verifier.verify('asdf', 'qwer')
        pybid_verifier.verify.assert_called_with('asdf', 'qwer')
        self.assertTrue(result)
        self.assertEqual(result._response, response)


    def test_verify_lazy_audiences(self):
        """
        If audience is a lazily evaluated object, it should be
        materialized during verification.
        """

        pybid_verifier = Mock()
        self.verifier.pybid_verifier = pybid_verifier

        audiences = cycle(['http://url1', 'http://url2'])
        audience = lazy(lambda: next(audiences), str)()

        response = {'status': 'okay'}
        pybid_verifier.verify.return_value = response

        self.verifier.verify('asdf', audience)
        pybid_verifier.verify.assert_called_with('asdf', 'http://url1')
        pybid_verifier.verify.mock_reset()

        self.verifier.verify('asdf', audience)
        pybid_verifier.verify.assert_called_with('asdf', 'http://url2')
        pybid_verifier.verify.mock_reset()
