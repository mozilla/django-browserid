# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from mock import Mock
from pyquery import PyQuery as pq

from django_browserid.context_processors import browserid


class BrowserIDInfoTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_defaults(self):
        request = self.factory.get('/')
        request.user = object()
        info = browserid(request)['browserid_info']
        d = pq(info)

        info_div = d('#browserid-info')
        self.assertEqual(info_div.attr('data-user-email'), '')
        self.assertEqual(info_div.attr('data-request-args'), '{}')

        form = d('#browserid-form')
        self.assertEqual(form.attr('action'), '/browserid/login/')

    @override_settings(BROWSERID_REQUEST_ARGS={'siteName': 'asdf'})
    def test_custom_values(self):
        request = self.factory.get('/')
        request.user = Mock(email='a@example.com')
        info = browserid(request)['browserid_info']
        d = pq(info)

        info_div = d('#browserid-info')
        self.assertEqual(info_div.attr('data-user-email'), 'a@example.com')
        self.assertEqual(info_div.attr('data-request-args'),
                         '{"siteName": "asdf"}')

        form = d('#browserid-form')
        self.assertEqual(form.attr('action'), '/browserid/login/')
