# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.client import RequestFactory

from django_browserid.base import get_audience
from django_browserid.tests import patch_settings


class TestGetAudience(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch_settings(DEBUG=True, SITE_URL='http://example.com')
    def test_improperly_configured(self):
        # Raise ImproperlyConfigured if SITE_URL doesn't match the request's
        # URL and DEBUG = True.
        request = self.factory.post('/', SERVER_NAME='www.blah.com')
        with self.assertRaises(ImproperlyConfigured):
            get_audience(request)

    @patch_settings(DEBUG=True, SITE_URL='http://example.com')
    def test_properly_configured(self):
        # Return SITE_URL if it matches the request URL and DEBUG = True.
        request = self.factory.post('/', SERVER_NAME='example.com')
        self.assertEqual('http://example.com', get_audience(request))

    @patch_settings(DEBUG=False, SITE_URL='http://example.com')
    def test_improperly_configured_no_debug(self):
        # If the SITE_URL and request URL don't match, but DEBUG = False, return
        # SITE_URL.
        request = self.factory.post('/', SERVER_NAME='www.blah.com')
        self.assertEqual('http://example.com', get_audience(request))
