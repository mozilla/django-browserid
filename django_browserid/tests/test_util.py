import json

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from django.utils import six
from django.utils.functional import lazy

from django_browserid.tests import TestCase
from django_browserid.util import import_from_setting, LazyEncoder, same_origin


def _lazy_string():
    return 'blah'
lazy_string = lazy(_lazy_string, six.text_type)()


class TestLazyEncoder(TestCase):
    def test_lazy(self):
        thing = ['foo', lazy_string]
        thing_json = json.dumps(thing, cls=LazyEncoder)
        self.assertEqual('["foo", "blah"]', thing_json)


import_value = 1


class ImportFromSettingTests(TestCase):
    def test_no_setting(self):
        """If the setting doesn't exist, raise ImproperlyConfigured."""
        with self.assertRaises(ImproperlyConfigured):
            import_from_setting('DOES_NOT_EXIST')

    @override_settings(TEST_SETTING={})
    def test_invalid_import(self):
        """
        If the setting isn't a proper string, raise
        ImproperlyConfigured.
        """
        with self.assertRaises(ImproperlyConfigured):
            import_from_setting('TEST_SETTING')

    @override_settings(TEST_SETTING='does.not.exist')
    def test_error_importing(self):
        """
        If there is an error importing the module, raise
        ImproperlyConfigured.
        """
        with self.assertRaises(ImproperlyConfigured):
            import_from_setting('TEST_SETTING')

    @override_settings(TEST_SETTING='django_browserid.tests.test_util.missing_value')
    def test_missing_attribute(self):
        """
        If the module is imported, but the function isn't found, raise
        ImproperlyConfigured.
        """
        with self.assertRaises(ImproperlyConfigured):
            import_from_setting('TEST_SETTING')

    @override_settings(TEST_SETTING='django_browserid.tests.test_util.import_value')
    def test_existing_attribute(self):
        """
        If the module is imported and has the requested function,
        return it.
        """
        self.assertEqual(import_from_setting('TEST_SETTING'), 1)


class SameOriginTests(TestCase):
    def test_match(self):
        self.assertTrue(same_origin('https://example.com', 'https://example.com'))
        self.assertTrue(same_origin('https://example.com:80', 'https://example.com:80'))
        self.assertTrue(same_origin('https://example.com:80/different/path?query=4&five=6',
                                    'https://example.com:80/no/match#path'))

    def test_no_match(self):
        self.assertFalse(same_origin('http://example.com', 'http://example.org'))
        self.assertFalse(same_origin('https://example.com', 'http://example.com'))
        self.assertFalse(same_origin('http://example.com:443', 'http://example.com:80'))
