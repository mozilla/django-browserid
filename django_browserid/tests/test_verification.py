# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from contextlib import contextmanager

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User

from mock import ANY, patch

from django_browserid.base import verify
from django_browserid.tests import mock_browserid
from django_browserid.auth import BrowserIDBackend


assertion = 'foo.bar.baz'
audience = 'http://localhost:8000'


authenticate_kwargs = {
    'assertion': assertion,
    'audience': audience,
}


@contextmanager
def negative_assertion(fake_http_request, **kwargs):
    assertion = {
        u'status': u'failure'
    }
    assertion.update(kwargs)
    fake_http_request.expects_call().returns(assertion)
    yield


@patch('django_browserid.auth.BrowserIDBackend.authenticate')
def test_backend_authenticate(fake):
    # Test that the authentication backend is set up correctly.
    fake.return_value = None
    auth.authenticate(**authenticate_kwargs)
    fake.assert_called_with(**authenticate_kwargs)


@patch('django_browserid.auth.verify')
def test_backend_verify(fake):
    # Test that authenticate() calls verify().
    fake.return_value = False
    auth.authenticate(**authenticate_kwargs)
    fake.assert_called_with(assertion, audience, extra_params=None)


@mock_browserid(None)
def test_backend_verify_invalid_assertion():
    # Test that authenticate() returns None when credentials are bad.
    user = auth.authenticate(**authenticate_kwargs)
    assert user is None


@patch('django_browserid.auth.verify')
def test_auth_copes_with_false(verify):
    # Test that authenticate copes with False.
    verify.return_value = False
    assert BrowserIDBackend().authenticate(**authenticate_kwargs) is None


@mock_browserid('myemail@example.com')
def test_verify_correct_credentials():
    # Test that verify() returns assertion details when assertion is valid.
    verification = verify(assertion, audience)
    assert verification['status'] == 'okay'
    assert verification['email'] == 'myemail@example.com'


@patch.object(settings, 'BROWSERID_CREATE_USER', True, create=True)
@patch.object(settings, 'BROWSERID_USERNAME_ALGO', None, create=True)
@mock_browserid('bid_create@example.com')
def test_authenticate_create_user():
    # Test that automatic user creation works when enabled.
    User.objects.filter(email='bid_create@example.com').delete()
    ob = User.objects.filter(email='bid_create@example.com')
    assert ob.exists() is False
    auth.authenticate(**authenticate_kwargs)

    ob = User.objects.filter(email='bid_create@example.com')
    assert ob.exists() is True


def username_algo(email):
    return email.split('@')[0]


@patch.object(settings, 'BROWSERID_CREATE_USER', True, create=True)
@patch.object(settings, 'BROWSERID_USERNAME_ALGO', username_algo, create=True)
@mock_browserid('bid_alt_username@example.com')
def test_authenticate_create_user_with_alternate_username_algo():
    # Test that automatic user creation with an alternate username algo
    # works.
    user = auth.authenticate(**authenticate_kwargs)
    assert user.username == 'bid_alt_username'


@patch.object(settings, 'BROWSERID_CREATE_USER',
              'django_browserid.tests.fake_create_user', create=True)
@patch('django_browserid.tests.fake_create_user')
@mock_browserid('does.not.exist@example.org')
def test_authenticate_create_user_with_callable(fake):
    # Test that automatic user creation with a callable function name works
    fake.return_value = None
    auth.authenticate(**authenticate_kwargs)
    fake.assert_called_with('does.not.exist@example.org')


@patch.object(settings, 'BROWSERID_CREATE_USER', False, create=True)
@mock_browserid('someotheremail@example.com')
def test_authenticate_missing_user():
     # Test that authenticate() returns None when user creation disabled.
    user = auth.authenticate(**authenticate_kwargs)
    assert user is None


@patch.object(settings, 'BROWSERID_HTTP_TIMEOUT', 1, create=True)
@patch.object(settings, 'BROWSERID_VERIFICATION_URL',
              'https://custom.org/verify', create=True)
@patch('django_browserid.base.requests.post')
def test_verify_post_uses_custom_settings(post):
    post.return_value.content = '{"status": "okay"}'
    verify(assertion, audience)
    post.assert_called_with('https://custom.org/verify',
                            verify=True,
                            proxies=ANY,
                            data=ANY,
                            timeout=1,
                            headers=ANY)


@patch('django_browserid.base.requests.post')
def test_verify_with_custom_url(post):
    post.return_value.content = '{"status": "okay"}'
    url = 'https://custom-service.org/verify'
    verify(assertion, audience, url=url)
    post.assert_called_with(url,
                            verify=ANY,
                            proxies=ANY,
                            data=ANY,
                            timeout=ANY,
                            headers=ANY)


@patch.object(settings, 'BROWSERID_ALLOW_UNVERIFIED', True, create=True)
@patch.object(settings, 'BROWSERID_VERIFICATION_URL', 'https://unverifier.persona.org/verify', create=True)
@mock_browserid(pass_mock=True)
def test_authenticate_unverified_user(_verify_http_request):
    """
    Test that extra parameters are passed through to _verify_http_request
    correctly.
    """
    # In real life, BROWSERID_VERIFICATION_URL would point to the
    # BID Unverified Email verifier. (Yes, that makes my head hurt too.)
    args = dict(authenticate_kwargs)
    args['extra_params'] = {
        'issuer': 'a.b.c',
        'allow_unverified': True,
        'first_name': u'P\xe3ter'
    }

    verify(**args)
    _verify_http_request.assert_called_once_with(
        'https://unverifier.persona.org/verify', ANY)
    assert _verify_http_request.call_args[0][1]['allow_unverified']
