import base64
import hashlib
import fudge

from contextlib import contextmanager

from django.conf import settings
from django.contrib import auth

from django_browserid import auth as browserid_auth

assertion = 'foo.bar.baz'
host = 'localhost'
port = '8000'

authenticate_kwargs = {
    'assertion': assertion,
    'host': host,
    'port': port
}


@contextmanager
def positive_assertion(fake_http_request, **kwargs):
    assertion = {
        u'audience': u'%s:%s' % (host, port),
        u'email': u'myemail@example.com',
        u'issuer': u'browserid.org:443',
        u'status': u'okay',
        u'valid-until': 1311377222765
    }
    assertion.update(kwargs)
    fake_http_request.expects_call().returns(assertion)
    yield


@contextmanager
def negative_assertion(fake_http_request, **kwargs):
    assertion = {
        u'status': u'failure'
    }
    assertion.update(kwargs)
    fake_http_request.expects_call().returns(assertion)
    yield


@fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
def test_backend_authenticate(fake):
    """Test that the authentication backend is set up correctly."""
    (fake.expects_call()
         .with_args(**authenticate_kwargs)
         .returns(None))
    auth.authenticate(**authenticate_kwargs)


@fudge.patch('django_browserid.auth.BrowserIDBackend.verify')
def test_backend_verify(fake):
    """Test that authenticate() calls verify()."""
    (fake.expects_call()
         .with_args(assertion, u'%s:%s' % (host, port))
         .returns(False))
    auth.authenticate(**authenticate_kwargs)


@fudge.patch('django_browserid.auth.BrowserIDBackend._verify_http_request')
def test_backend_verify_invalid_assertion(fake):
    """Test that authenticate() returns None when credentials are bad."""
    with negative_assertion(fake):
        user = auth.authenticate(**authenticate_kwargs)
        assert user is None


@fudge.patch('django_browserid.auth.BrowserIDBackend._verify_http_request')
def test_verify_correct_credentials(fake):
    """Test that verify() returns assertion details when assertion is valid."""
    with positive_assertion(fake):
        backend = browserid_auth.BrowserIDBackend()
        verification = backend.verify(assertion, u'%s:%s' % (host, port))
        assert verification['status'] == 'okay'
        assert verification['email'] == 'myemail@example.com'


@fudge.patch('django_browserid.auth.BrowserIDBackend._verify_http_request')
def test_authenticate_create_user(fake):
    """Test that automatic user creation works when enabled."""
    with positive_assertion(fake):
        setattr(settings, 'BROWSERID_CREATE_USER', True)
        user = auth.authenticate(**authenticate_kwargs)
        # user should have been created
        assert user
        assert user.email == 'myemail@example.com'
        assert user.username == base64.urlsafe_b64encode(
            hashlib.sha1(user.email).digest()).rstrip('=')


@fudge.patch('django_browserid.auth.BrowserIDBackend._verify_http_request')
def test_authenticate_missing_user(fake):
    """Test that authenticate() returns None when user creation disabled."""
    with positive_assertion(fake, email='someotheremail@example.com'):
        setattr(settings, 'BROWSERID_CREATE_USER', False)
        user = auth.authenticate(**authenticate_kwargs)
        assert user is None
