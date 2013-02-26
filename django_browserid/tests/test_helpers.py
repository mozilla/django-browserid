from django.test import TestCase

from mock import patch
from pyquery import PyQuery as pq

from django_browserid.helpers import browserid_button, browserid_js


@patch('django_browserid.helpers.FORM_JAVASCRIPT',
       ('test1.js', 'test2.js'))
@patch('django_browserid.helpers.BROWSERID_SHIM',
       'https://example.com/test3.js')
class BrowserIDJSTests(TestCase):
    def test_basic(self):
        output = browserid_js().strip()
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
