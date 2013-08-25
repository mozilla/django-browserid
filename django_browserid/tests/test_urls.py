from django.core.urlresolvers import resolve
from django.test import TestCase
from django.test.client import RequestFactory

from mock import Mock
try:
    from imp import reload
except ImportError:
    # In Python 2.x, this was a builtin, but in 3.x, it's in the imp module.
    pass

from django_browserid.tests import patch_settings
from django_browserid import urls


MyVerifyClass = Mock()


class UrlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_override_verify_class(self):
        # Reload so that the settings.BROWSERID_VERIFY_CLASS takes effect.
        path = 'django_browserid.tests.test_urls.MyVerifyClass'
        with patch_settings(BROWSERID_VERIFY_CLASS=path):
            reload(urls)

        view = resolve('/login/', urls).func
        self.assertEqual(view, MyVerifyClass.as_view())

        # Reset urls back to normal.
        reload(urls)
