# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.client import RequestFactory

import requests
import six
from mock import Mock, patch, PropertyMock
from nose.tools import eq_, ok_

from django_browserid.base import (BrowserIDException, get_audience, MockVerifier, RemoteVerifier,
                                   VerificationResult)
from django_browserid.tests import patch_settings


class GetAudienceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_setting_missing(self):
        # If BROWSERID_AUDIENCES isn't defined, raise ImproperlyConfigured.
        request = self.factory.get('/')

        # Simulate missing attribute with a mock property that raises AttributeError.
        with patch('django_browserid.base.settings') as settings:
            mock_browserid_audiences = PropertyMock(side_effect=AttributeError)
            type(settings).BROWSERID_AUDIENCES = mock_browserid_audiences

            with self.assertRaises(ImproperlyConfigured):
                get_audience(request)

    def test_same_origin_found(self):
        # If an audience is found in BROWSERID_AUDIENCES with the same origin as the request URI,
        # return it.
        request = self.factory.get('http://testserver')

        audiences = ['https://example.com', 'http://testserver']
        with patch_settings(BROWSERID_AUDIENCES=audiences):
            eq_(get_audience(request), 'http://testserver')

    def test_no_audience(self):
        # If no matching audiences is found in BROWSERID_AUDIENCES, raise ImproperlyConfigured.
        request = self.factory.get('http://testserver')

        with patch_settings(BROWSERID_AUDIENCES=['https://example.com']):
            with self.assertRaises(ImproperlyConfigured):
                get_audience(request)


class VerificationResultTests(TestCase):
    def test_getattr_attribute_exists(self):
        # If a value exists in the response dict, it should be an attribute on the result.
        result = VerificationResult({'myattr': 'foo'})
        eq_(result.myattr, 'foo')

    def test_getattr_attribute_doesnt_exist(self):
        # If a value doesn't exist in the response dict, accessing it as an attribute should raise
        # an AttributeError.
        result = VerificationResult({'myattr': 'foo'})
        with self.assertRaises(AttributeError):
            result.bar

    def test_expires_no_attribute(self):
        # If no expires attribute was in the response, raise an AttributeError.
        result = VerificationResult({'myattr': 'foo'})
        with self.assertRaises(AttributeError):
            result.expires

    def test_expires_invalid_timestamp(self):
        # If the expires attribute cannot be parsed as a timestamp, return the raw string instead.
        result = VerificationResult({'expires': 'foasdfhas'})
        eq_(result.expires, 'foasdfhas')

    def test_expires_valid_timestamp(self):
        # If expires contains a valid millisecond timestamp, return a corresponding datetime.
        result = VerificationResult({'expires': '1379307128000'})
        eq_(datetime(2013, 9, 16, 4, 52, 8), result.expires)

    def test_nonzero_failure(self):
        # If the response status is not 'okay', the result should be falsy.
        ok_(not VerificationResult({'status': 'failure'}))

    def test_nonzero_okay(self):
        # If the response status is 'okay', the result should be truthy.
        ok_(VerificationResult({'status': 'okay'}))

    def test_str_success(self):
        # If the result is successful, include 'Success' and the email in the string.
        result = VerificationResult({'status': 'okay', 'email': 'a@example.com'})
        eq_(six.text_type(result), '<VerificationResult Success email=a@example.com>')

        # If the email is missing, don't include it.
        result = VerificationResult({'status': 'okay'})
        eq_(six.text_type(result), '<VerificationResult Success>')

    def test_str_failure(self):
        # If the result is a failure, include 'Failure' in the string.
        result = VerificationResult({'status': 'failure'})
        eq_(six.text_type(result), '<VerificationResult Failure>')


class RemoteVerifierTests(TestCase):
    def _response(self, **kwargs):
        return Mock(spec=requests.Response, **kwargs)

    def test_verify_requests_parameters(self):
        # If a subclass overrides requests_parameters, the parameters should be passed to
        # requests.post.
        class MyVerifier(RemoteVerifier):
            requests_parameters = {'foo': 'bar'}
        verifier = MyVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{"status":"failure"}')
            verifier.verify('asdf', 'http://testserver')

        # foo parameter passed with 'bar' value.
        eq_(post.call_args[1]['foo'], 'bar')

    def test_verify_kwargs(self):
        # Any keyword arguments passed to verify should be passed on as POST arguments.
        verifier = RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{"status":"failure"}')
            verifier.verify('asdf', 'http://testserver', foo='bar', baz=5)

        # foo parameter passed with 'bar' value.
        eq_(post.call_args[1]['data']['foo'], 'bar')
        eq_(post.call_args[1]['data']['baz'], 5)

    def test_verify_request_exception(self):
        # If a RequestException is raised during the POST, raise a BrowserIDException with the
        # RequestException as the cause.
        verifier = RemoteVerifier()
        request_exception = requests.exceptions.RequestException()

        with patch('django_browserid.base.requests.post') as post:
            post.side_effect = request_exception
            with self.assertRaises(BrowserIDException) as cm:
                verifier.verify('asdf', 'http://testserver')

        eq_(cm.exception.exc, request_exception)

    def test_verify_invalid_json(self):
        # If the response contains invalid JSON, return a failure result.
        verifier = RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(content='{asg9=3{{{}}{')
            result = verifier.verify('asdf', 'http://testserver')
        ok_(not result)
        ok_(result.reason.startswith('Could not parse verifier response'))


    def test_verify_success(self):
        # If the response contains valid JSON, return a result object for that response.
        verifier = RemoteVerifier()

        with patch('django_browserid.base.requests.post') as post:
            post.return_value = self._response(
                content='{"status": "okay", "email": "foo@example.com"}')
            result = verifier.verify('asdf', 'http://testserver')
        ok_(result)
        eq_(result.email, 'foo@example.com')


class MockVerifierTests(TestCase):
    def test_verify_no_email(self):
        # If the given email is None, verify should return a failure result.
        verifier = MockVerifier(None)
        result = verifier.verify('asdf', 'http://testserver')
        ok_(not result)
        eq_(result.reason, 'No email given to MockVerifier.')

    def test_verify_email(self):
        # If an email is given to the constructor, return a successful result.
        verifier = MockVerifier('a@example.com')
        result = verifier.verify('asdf', 'http://testserver')
        ok_(result)
        eq_(result.audience, 'http://testserver')
        eq_(result.email, 'a@example.com')

    def test_verify_result_attributes(self):
        # Extra kwargs to the constructor are added to the result.
        verifier = MockVerifier('a@example.com', foo='bar', baz=5)
        result = verifier.verify('asdf', 'http://testserver')
        eq_(result.foo, 'bar')
        eq_(result.baz, 5)
