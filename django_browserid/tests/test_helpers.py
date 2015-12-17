from django.utils.functional import lazy

from mock import patch

from django_browserid import helpers
from django_browserid.tests import JSON_STRING, TestCase


def _lazy_request_args():
    return {'siteName': 'asdf'}
lazy_request_args = lazy(_lazy_request_args, dict)


class BrowserIDInfoTests(TestCase):
    def setUp(self):
        patcher = patch('django_browserid.helpers.render_to_string')
        self.addCleanup(patcher.stop)
        self.render_to_string = patcher.start()

    def test_defaults(self):
        with self.settings(BROWSERID_REQUEST_ARGS={'foo': 'bar', 'baz': 1}):
            output = helpers.browserid_info()

        self.assertEqual(output, self.render_to_string.return_value)
        expected_info = JSON_STRING({
            'loginUrl': '/browserid/login/',
            'logoutUrl': '/browserid/logout/',
            'csrfUrl': '/browserid/csrf/',
            'requestArgs': {'foo': 'bar', 'baz': 1},
        })
        self.render_to_string.assert_called_with('browserid/info.html', {'info': expected_info})

    def test_lazy_request_args(self):
        with self.settings(BROWSERID_REQUEST_ARGS=lazy_request_args()):
            output = helpers.browserid_info()

        self.assertEqual(output, self.render_to_string.return_value)
        expected_info = JSON_STRING({
            'loginUrl': '/browserid/login/',
            'logoutUrl': '/browserid/logout/',
            'csrfUrl': '/browserid/csrf/',
            'requestArgs': {'siteName': 'asdf'},
        })
        self.render_to_string.assert_called_with('browserid/info.html', {'info': expected_info})


class BrowserIDJSTests(TestCase):
    def test_basic(self):
        output = helpers.browserid_js()
        self.assertHTMLEqual(output, """
            <script type="text/javascript" src="https://login.persona.org/include.js"></script>
            <script type="text/javascript" src="static/browserid/api.js"></script>
            <script type="text/javascript" src="static/browserid/browserid.js"></script>
        """)

    def test_no_shim(self):
        output = helpers.browserid_js(include_shim=False)
        self.assertHTMLEqual(output, """
            <script type="text/javascript" src="static/browserid/api.js"></script>
            <script type="text/javascript" src="static/browserid/browserid.js"></script>
        """)

    def test_custom_shim(self):
        with self.settings(BROWSERID_SHIM='http://example.com/test.js'):
            output = helpers.browserid_js()
        self.assertHTMLEqual(output, """
            <script type="text/javascript" src="http://example.com/test.js"></script>
            <script type="text/javascript" src="static/browserid/api.js"></script>
            <script type="text/javascript" src="static/browserid/browserid.js"></script>
        """)

    def test_autologin_email(self):
        """
        If BROWSERID_AUTOLOGIN_ENABLED is True, do not include the shim
        and include the autologin mock script.
        """
        with self.settings(BROWSERID_AUTOLOGIN_ENABLED=True):
            output = helpers.browserid_js()
            self.assertHTMLEqual(output, """
                <script type="text/javascript" src="static/browserid/api.js"></script>
                <script type="text/javascript" src="static/browserid/autologin.js"></script>
                <script type="text/javascript" src="static/browserid/browserid.js"></script>
            """)


class BrowserIDCSSTests(TestCase):
    def test_basic(self):
        output = helpers.browserid_css()
        self.assertHTMLEqual(output, """
            <link rel="stylesheet" href="static/browserid/persona-buttons.css" />
        """)


class BrowserIDButtonTests(TestCase):
    def test_basic(self):
        button = helpers.browserid_button(text='asdf', next='1234', link_class='fake-button',
                                          href="/test", attrs={'target': '_blank'})
        self.assertHTMLEqual(button, """
            <a href="/test" class="fake-button" data-next="1234" target="_blank">
                <span>asdf</span>
            </a>
        """)

    def test_json_attrs(self):
        button = helpers.browserid_button(text='qwer', next='5678', link_class='fake-button',
                                          attrs='{"target": "_blank"}')
        self.assertHTMLEqual(button, """
            <a href="#" class="fake-button" data-next="5678" target="_blank">
                <span>qwer</span>
            </a>
        """)


class BrowserIDLoginTests(TestCase):
    def test_login_class(self):
        button = helpers.browserid_login(link_class='go button')
        self.assertHTMLEqual(button, """
            <a href="#" class="go button browserid-login" data-next="">
                <span>Sign in</span>
            </a>
        """)

    def test_default_class(self):
        """
        If no class is provided, it should default to
        'browserid-login persona-button'.
        """
        button = helpers.browserid_login()
        self.assertHTMLEqual(button, """
            <a href="#" class="browserid-login persona-button" data-next="">
                <span>Sign in</span>
            </a>
        """)

    def test_color_class(self):
        button = helpers.browserid_login(color='dark')
        self.assertHTMLEqual(button, """
            <a href="#" class="browserid-login persona-button dark" data-next="">
                <span>Sign in</span>
            </a>
        """)

    def test_color_custom_class(self):
        """
        If using a color and a custom link class, persona-button should
        be added to the link class.
        """
        button = helpers.browserid_login(link_class='go button', color='dark')
        self.assertHTMLEqual(button, """
            <a href="#" class="go button browserid-login persona-button dark" data-next="">
                <span>Sign in</span>
            </a>
        """)

    def test_next(self):
        button = helpers.browserid_login(next='/foo/bar')
        self.assertHTMLEqual(button, """
            <a href="#" class="browserid-login persona-button" data-next="/foo/bar">
                <span>Sign in</span>
            </a>
        """)


class BrowserIDLogoutTests(TestCase):
    def test_logout_class(self):
        button = helpers.browserid_logout(link_class='go button')
        self.assertHTMLEqual(button, """
            <a href="/browserid/logout/" class="go button browserid-logout" data-next="">
                <span>Sign out</span>
            </a>
        """)

    def test_next(self):
        button = helpers.browserid_logout(next='/foo/bar')
        self.assertHTMLEqual(button, """
            <a href="/browserid/logout/" class="browserid-logout" data-next="/foo/bar">
                <span>Sign out</span>
            </a>
        """)
