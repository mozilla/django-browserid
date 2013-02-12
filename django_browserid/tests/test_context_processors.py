from django.test import TestCase
from django.test.client import RequestFactory

from mock import Mock, patch
from pyquery import PyQuery as pq

from django_browserid.context_processors import browserid_button, browserid_js


class DummyForm(object):
    class DummyMedia(object):
        def absolute_path(self, path):
            return path
    media = DummyMedia()


@patch('django_browserid.context_processors.FORM_JAVASCRIPT',
       ('test1.js', 'test2.js'))
@patch('django_browserid.context_processors.BROWSERID_SHIM', 'test3.js')
class BrowserIDJSTests(TestCase):
    def test_basic(self):
        output = browserid_js(DummyForm()).strip()
        self.assertTrue('src="test1.js"' in output)
        self.assertTrue('src="test2.js"' in output)
        self.assertTrue('src="test3.js"' in output)

    def test_no_shim(self):
        output = browserid_js(DummyForm(), include_shim=False)
        self.assertTrue('src="test1.js"' in output)
        self.assertTrue('src="test2.js"' in output)
        self.assertTrue('src="test3.js"' not in output)

    def test_absolute_path(self):
        mock_form = Mock()
        browserid_js(mock_form)
        mock_form.media.absolute_path.assert_any_call('test1.js')
        mock_form.media.absolute_path.assert_any_call('test2.js')
        mock_form.media.absolute_path.assert_any_call('test3.js')


class BrowserIDButtonTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('django_browserid.context_processors.render_to_string')
    def test_request_args_dict(self, render_to_template):
        """
        If request_args is a dict, it must be passed to the template as a JSON
        string.
        """
        request = self.factory.get('/')
        browserid_button(request, request_args={'siteName': 'test'})
        self.assertEqual(render_to_template.call_args[0][1]['request_args'],
                         '{"siteName": "test"}')

    @patch('django_browserid.context_processors.render_to_string')
    def test_request_args_string(self, render_to_template):
        """
        If request_args is a string, it must be escaped and passed to the
        template.
        """
        request = self.factory.get('/')
        browserid_button(request, request_args='{"siteName": "test"}')
        self.assertEqual(render_to_template.call_args[0][1]['request_args'],
                         '{&quot;siteName&quot;: &quot;test&quot;}')

    def test_form_extras(self):
        """form_extras should be rendered as hidden inputs in the button."""
        request = self.factory.get('/')
        button = browserid_button(request, form_extras={'test': 'blah'})
        d = pq(button)
        hidden_input = d('form.browserid-form input[name="test"]')
        self.assertEqual(hidden_input.val(), 'blah')

    def test_link_class(self):
        """link_class should control the class attribute on the link."""
        request = self.factory.get('/')
        button = browserid_button(request, link_class='blah goo')
        d = pq(button)
        link = d('a')
        self.assertTrue(link.hasClass('blah'))
        self.assertTrue(link.hasClass('goo'))
        self.assertTrue(link.hasClass('browserid-login'))

