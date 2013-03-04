# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.client import RequestFactory

from mock import patch
from requests.exceptions import RequestException

from django_browserid.base import BrowserIDException, get_audience, verify
from django_browserid.tests import patch_settings


class TestGetAudience(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch_settings(SITE_URL='http://example.com')
    def test_improperly_configured(self):
        # Raise ImproperlyConfigured if SITE_URL doesn't match the request's
        # URL.
        request = self.factory.post('/', SERVER_NAME='www.blah.com')
        with self.assertRaises(ImproperlyConfigured):
            get_audience(request)

    @patch_settings(SITE_URL='http://example.com')
    def test_properly_configured(self):
        # Return SITE_URL if it matches the request URL and DEBUG = True.
        request = self.factory.post('/', SERVER_NAME='example.com')
        self.assertEqual('http://example.com', get_audience(request))

    @patch_settings(DEBUG=True)
    def test_no_site_url(self):
        # If SITE_URL isn't set, use the domain from the request.
        request = self.factory.post('/', SERVER_NAME='www.blah.com')
        self.assertEqual('http://www.blah.com', get_audience(request))


class VerifyTests(TestCase):
    @patch('django_browserid.base.requests')
    def test_browserid_exception(self, requests):
        """
        If requests.post raises an exception, wrap it in a BrowserIDException.
        """
        requests.post.side_effect = RequestException
        requests.exceptions.RequestException = RequestException

        with self.assertRaises(BrowserIDException):
            verify('asdf', 'http://testserver/')
