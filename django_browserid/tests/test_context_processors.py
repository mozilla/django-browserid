from django.test import TestCase

from mock import Mock, patch

from django_browserid.context_processors import browserid_js


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
