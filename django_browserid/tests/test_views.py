"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django.conf import settings
from django.contrib import auth
from django.test.client import RequestFactory

from mock import patch

from django_browserid import views
from django_browserid.tests import mock_browserid


factory = RequestFactory()


def verify(request_type, redirect_field_name=None, success_url=None,
           failure_url=None, **kwargs):
    """Call the verify view function. All kwargs not specified above will be
    passed as GET or POST arguments.
    """
    if request_type == 'get':
        request = factory.get('/browserid/verify', kwargs)
    else:
        request = factory.post('/browserid/verify', kwargs)

    # Patch settings prior to importing verify
    patches = []
    if success_url is not None:
        patches.append(patch.object(settings, 'LOGIN_REDIRECT_URL',
                                    success_url, create=True))
    if failure_url is not None:
        patches.append(patch.object(settings, 'LOGIN_REDIRECT_URL_FAILURE',
                                    failure_url, create=True))
    # Create users if they don't exist for testing.
    patches.append(patch.object(settings, 'BROWSERID_CREATE_USER', True,
                                create=True))

    # Only pass redirect_field_name if it is specified
    verify_kwargs = {}
    if redirect_field_name is not None:
        verify_kwargs['redirect_field_name'] = redirect_field_name

    for p in patches:
        p.start()

    # We need to reload verify for the setting changes to take effect.
    reload(views)
    verify_view = views.Verify.as_view()
    with patch.object(auth, 'login'):
        response = verify_view(request, **verify_kwargs)

    for p in patches:
        p.stop()

    return response


def test_get_redirect_failure():
    """Issuing a GET to the verify view redirects to the failure URL."""
    response = verify('get', failure_url='/fail')
    assert response.status_code == 302
    assert response['Location'].endswith('/fail')


def test_invalid_redirect_failure():
    """Invalid form arguments redirect to the failure URL."""
    response = verify('post', failure_url='/fail', blah='asdf')
    assert response.status_code == 302
    assert response['Location'].endswith('/fail')


@mock_browserid(None)
def test_auth_fail_redirect_failure():
    """If authentication fails, redirect to the failure URL."""
    response = verify('post', failure_url='/fail', assertion='asdf')
    assert response.status_code == 302
    assert response['Location'].endswith('/fail')


@mock_browserid('test@example.com')
def test_auth_success_redirect_success():
    """If authentication succeeds, redirect to the success URL."""
    response = verify('post', success_url='/success', assertion='asdf')
    assert response.status_code == 302
    assert response['Location'].endswith('/success')


@mock_browserid('test@example.com')
def test_default_redirect_field():
    """If a redirect is passed as an argument to the request, redirect to that
    instead of the success URL.
    """
    kwargs = {auth.REDIRECT_FIELD_NAME: '/field_success', 'assertion': 'asdf'}
    response = verify('post', success_url='/success', **kwargs)
    assert response.status_code == 302
    assert response['Location'].endswith('/field_success')


@mock_browserid('test@example.com')
def test_redirect_field_name():
    """If a redirect field name is specified, use the request argument matching
    that name as the path to redirect to.
    """
    kwargs = {'my_redirect': '/field_success', 'assertion': 'asdf'}
    response = verify('post', success_url='/success',
                      redirect_field_name='my_redirect', **kwargs)
    assert response.status_code == 302
    assert response['Location'].endswith('/field_success')
