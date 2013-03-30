from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.test.client import RequestFactory

from mock import patch
from pyquery import PyQuery as pq

from django_browserid.helpers import (browserid_button, browserid_image_link,
                                      browserid_info, browserid_js,
                                      browserid_login, browserid_logout)
from django_browserid.tests import patch_settings


@patch('django_browserid.helpers.FORM_JAVASCRIPT',
       ('test1.js', 'test2.js'))
@patch('django_browserid.helpers.BROWSERID_SHIM',
       'https://example.com/test3.js')
class BrowserIDJSTests(TestCase):
    def test_basic(self):
        output = browserid_js()
        self.assertTrue('src="static/test1.js"' in output)
        self.assertTrue('src="static/test2.js"' in output)
        self.assertTrue('src="https://example.com/test3.js"' in output)

    def test_no_shim(self):
        output = browserid_js(include_shim=False)
        self.assertTrue('src="static/test1.js"' in output)
        self.assertTrue('src="static/test2.js"' in output)
        self.assertTrue('src="https://example.com/test3.js"' not in output)


class BrowserIDButtonTests(TestCase):
    def test_basic(self):
        button = browserid_button(text='asdf', next='1234',
                                  link_class='fake-button',
                                  attrs={'target': '_blank'})
        a = pq(button)('a')

        self.assertTrue(a.hasClass('fake-button'))
        self.assertEqual(a.attr('href'), '#')
        self.assertEqual(a.attr('data-next'), '1234')
        self.assertEqual(a.text(), 'asdf')
        self.assertEqual(a.attr('target'), '_blank')

    def test_json_attrs(self):
        button = browserid_button(text='qwer', next='5678',
                                  link_class='fake-button',
                                  attrs='{"target": "_blank"}')
        a = pq(button)('a')

        self.assertTrue(a.hasClass('fake-button'))
        self.assertEqual(a.attr('href'), '#')
        self.assertEqual(a.attr('data-next'), '5678')
        self.assertEqual(a.attr('target'), '_blank')
        self.assertEqual(a.text(), 'qwer')

    def test_login_class(self):
        # If browserid-login isn't in the link_class argument, it should be
        # appended to it prior to calling browserid_button.
        button = browserid_login(link_class='go button')
        a = pq(button)('a')

        self.assertTrue(a.hasClass('browserid-login'))

    def test_logout_class(self):
        # If browserid-logout isn't in the link_class argument, it should be
        # appended to it prior to calling browserid_button.
        button = browserid_logout(link_class='go button')
        a = pq(button)('a')

        self.assertTrue(a.hasClass('browserid-logout'))

    def test_image(self):
        button = browserid_login(image='plain_sign_in_red.png', next='1234',
                                      link_class='fake-button',
                                      attrs={'target': '_blank'})
        a = pq(button)('a')
        img = pq(button)('img')

        self.assertTrue(a.hasClass('fake-button'))
        self.assertEqual(a.attr('href'), '#')
        self.assertEqual(a.attr('data-next'), '1234')
        self.assertEqual(a.text(), '')
        self.assertEqual(a.attr('target'), '_blank')
        self.assertEqual(img.attr('src'), 'static/browserid/plain_sign_in_red.png')
    

class BrowserIDInfoTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_defaults(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        info = browserid_info(request)
        d = pq(info)

        info_div = d('#browserid-info')
        self.assertEqual(info_div.attr('data-user-email'), '')
        self.assertEqual(info_div.attr('data-request-args'), '{}')

        form = d('#browserid-form')
        self.assertEqual(form.attr('action'), '/browserid/login/')

    @patch_settings(BROWSERID_REQUEST_ARGS={'siteName': 'asdf'})
    def test_custom_values(self):
        request = self.factory.get('/')
        request.user = User.objects.create_user('asdf', 'a@example.com')
        info = browserid_info(request)
        d = pq(info)

        info_div = d('#browserid-info')
        self.assertEqual(info_div.attr('data-user-email'), 'a@example.com')
        self.assertEqual(info_div.attr('data-request-args'),
                         '{"siteName": "asdf"}')

        form = d('#browserid-form')
        self.assertEqual(form.attr('action'), '/browserid/login/')
