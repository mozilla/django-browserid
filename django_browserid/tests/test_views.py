# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import auth
from django.middleware.csrf import get_token, rotate_token
from django.test.client import RequestFactory
from django.utils import six

from mock import Mock, patch

from django_browserid import views
from django_browserid.tests import mock_browserid, TestCase


class JSONViewTests(TestCase):
    def test_http_method_not_allowed(self):
        class TestView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'
        response = TestView().http_method_not_allowed()
        self.assertEqual(response.status_code, 405)
        self.assertTrue(set(['GET']).issubset(set(response['Allow'].split(', '))))
        self.assert_json_equals(response.content, {'error': 'Method not allowed.'})

    def test_http_method_not_allowed_allowed_methods(self):
        class GetPostView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'

            def post(self, request, *args, **kwargs):
                return 'qwer'
        response = GetPostView().http_method_not_allowed()
        self.assertTrue(set(['GET', 'POST']).issubset(set(response['Allow'].split(', '))))

        class GetPostPutDeleteHeadView(views.JSONView):
            def get(self, request, *args, **kwargs):
                return 'asdf'

            def post(self, request, *args, **kwargs):
                return 'qwer'

            def put(self, request, *args, **kwargs):
                return 'qwer'

            def delete(self, request, *args, **kwargs):
                return 'qwer'

            def head(self, request, *args, **kwargs):
                return 'qwer'
        response = GetPostPutDeleteHeadView().http_method_not_allowed()
        expected_methods = set(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
        actual_methods = set(response['Allow'].split(', '))
        self.assertTrue(expected_methods.issubset(actual_methods))


class GetNextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_param(self):
        """If next isn't in the POST params, return None."""
        request = self.factory.post('/')
        self.assertEqual(views._get_next(request), None)

    def test_is_safe(self):
        """Return the value of next if it is considered safe."""
        request = self.factory.post('/', {'next': '/asdf'})
        request.get_host = lambda: 'myhost'

        with patch.object(views, 'is_safe_url', return_value=True) as is_safe_url:
            self.assertEqual(views._get_next(request), '/asdf')
            is_safe_url.assert_called_with('/asdf', host='myhost')

    def test_isnt_safe(self):
        """If next isn't safe, return None."""
        request = self.factory.post('/', {'next': '/asdf'})
        request.get_host = lambda: 'myhost'

        with patch.object(views, 'is_safe_url', return_value=False) as is_safe_url:
            self.assertEqual(views._get_next(request), None)
            is_safe_url.assert_called_with('/asdf', host='myhost')


class VerifyTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def verify(self, request_type, **kwargs):
        """
        Call the verify view function. Kwargs are passed as GET or POST
        arguments.
        """
        if request_type == 'get':
            request = self.factory.get('/browserid/verify', kwargs)
        else:
            request = self.factory.post('/browserid/verify', kwargs)

        verify_view = views.Verify.as_view()
        with patch.object(auth, 'login'):
            response = verify_view(request)

        return response

    def test_no_assertion(self):
        """If no assertion is given, return a failure result."""
        with self.settings(LOGIN_REDIRECT_URL_FAILURE='/fail'):
            response = self.verify('post', blah='asdf')
        self.assertEqual(response.status_code, 403)
        self.assert_json_equals(response.content, {'redirect': '/fail'})

    @mock_browserid(None)
    def test_auth_fail(self):
        """If authentication fails, redirect to the failure URL."""
        with self.settings(LOGIN_REDIRECT_URL_FAILURE='/fail'):
            response = self.verify('post', assertion='asdf')
        self.assertEqual(response.status_code, 403)
        self.assert_json_equals(response.content, {'redirect': '/fail'})

    @mock_browserid(None)
    def test_auth_fail_named_url(self):
        """
        If authentication fails, redirect to the failure URL, and resolve
        named URLs.
        """
        with self.settings(LOGIN_REDIRECT_URL_FAILURE='test_url'):
            response = self.verify('post', assertion='asdf')
        self.assertEqual(response.status_code, 403)
        self.assert_json_equals(response.content, {'redirect': '/some-dummy-url/'})

    @mock_browserid('test@example.com')
    def test_auth_success_redirect_success(self):
        """If authentication succeeds, redirect to the success URL."""
        user = auth.models.User.objects.create_user('asdf', 'test@example.com')

        request = self.factory.post('/browserid/verify', {'assertion': 'asdf'})
        with self.settings(LOGIN_REDIRECT_URL='/success'):
            with patch('django_browserid.views.auth.login') as login:
                verify = views.Verify.as_view()
                response = verify(request)

        login.assert_called_with(request, user)
        self.assertEqual(response.status_code, 200)
        self.assert_json_equals(response.content,
                                {'email': 'test@example.com', 'redirect': '/success'})

    @mock_browserid('test@example.com')
    def test_auth_success_redirect_success_named_url(self):
        """
        If authentication succeeds, redirect to the success URL, and resolve
        named urls.
        """
        user = auth.models.User.objects.create_user('asdf', 'test@example.com')

        request = self.factory.post('/browserid/verify', {'assertion': 'asdf'})
        with self.settings(LOGIN_REDIRECT_URL='test_url'):
            with patch('django_browserid.views.auth.login') as login:
                verify = views.Verify.as_view()
                response = verify(request)
        self.assertEqual(response.status_code, 200)
        self.assert_json_equals(response.content,
                                {'email': 'test@example.com', 'redirect': '/some-dummy-url/'})

    def test_sanity_checks(self):
        """Run sanity checks on all incoming requests."""
        with patch('django_browserid.views.sanity_checks') as sanity_checks:
            self.verify('post')
        self.assertTrue(sanity_checks.called)

    @patch('django_browserid.views.auth.login')
    def test_login_success_no_next(self, *args):
        """
        If _get_next returns None, use success_url for the redirect
        parameter.
        """
        view = views.Verify()
        view.request = self.factory.post('/')
        view.user = Mock(email='a@b.com')

        with patch('django_browserid.views._get_next', return_value=None) as _get_next:
            with patch.object(views.Verify, 'success_url', '/?asdf'):
                response = view.login_success()

        self.assert_json_equals(response.content, {'email': 'a@b.com', 'redirect': '/?asdf'})
        _get_next.assert_called_with(view.request)

    @patch('django_browserid.views.auth.login')
    def test_login_success_next(self, *args):
        """
        If _get_next returns a URL, use it for the redirect parameter.
        """
        view = views.Verify()
        view.request = self.factory.post('/')
        view.user = Mock(email='a@b.com')

        with patch('django_browserid.views._get_next', return_value='/?qwer') as _get_next:
            with patch.object(views.Verify, 'success_url', '/?asdf'):
                response = view.login_success()

        self.assert_json_equals(response.content, {'email': 'a@b.com', 'redirect': '/?qwer'})
        _get_next.assert_called_with(view.request)


class LogoutTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        _get_next_patch = patch('django_browserid.views._get_next')
        self._get_next = _get_next_patch.start()
        self.addCleanup(_get_next_patch.stop)

    def test_redirect(self):
        """Include LOGOUT_REDIRECT_URL in the response."""
        request = self.factory.post('/')
        logout = views.Logout.as_view()
        self._get_next.return_value = None

        with patch.object(views.Logout, 'redirect_url', '/test/foo'):
            with patch('django_browserid.views.auth.logout') as auth_logout:
                response = logout(request)

        auth_logout.assert_called_with(request)
        self.assertEqual(response.status_code, 200)
        self.assert_json_equals(response.content, {'redirect': '/test/foo'})

    def test_redirect_named_url(self):
        """
        Include LOGOUT_REDIRECT_URL in the response, and resolve named URLs.
        """
        request = self.factory.post('/')
        logout = views.Logout.as_view()
        self._get_next.return_value = None

        with self.settings(LOGOUT_REDIRECT_URL='test_url'):
            with patch('django_browserid.views.auth.logout') as auth_logout:
                response = logout(request)
        self.assertEqual(response.status_code, 200)
        self.assert_json_equals(response.content, {'redirect': '/some-dummy-url/'})

    def test_redirect_next(self):
        """
        If _get_next returns a URL, use it for the redirect parameter.
        """
        request = self.factory.post('/')
        logout = views.Logout.as_view()
        self._get_next.return_value = '/test/bar'

        with patch.object(views.Logout, 'redirect_url', '/test/foo'):
            with patch('django_browserid.views.auth.logout'):
                response = logout(request)

        self.assert_json_equals(response.content, {'redirect': '/test/bar'})


class CsrfTokenTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = views.CsrfToken()

    def test_session_csrf(self):
        request = self.factory.get('/browserid/csrf/')
        request.csrf_token = 'asdf'

        response = self.view.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'asdf')

    def test_django_csrf(self):
        request = self.factory.get('/browserid/csrf/')
        rotate_token(request)
        token = get_token(request)

        response = self.view.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, six.b(token))

    def test_never_cache(self):
        request = self.factory.get('/browserid/csrf/')
        response = self.view.get(request)
        self.assertTrue('max-age=0' in response['Cache-Control'])
