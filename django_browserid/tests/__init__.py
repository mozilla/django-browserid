"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django.utils.functional import wraps

from mock import patch


def fake_create_user(email):
    pass


class mock_browserid(object):
    """
    Mocks django_browserid verification. Can be used as a context manager or
    as a decorator:

    with mock_browserid('a@b.com'):
        django_browserid.verify('random-token')  # = {'status': 'okay',
                                                 #    'email': 'a@b.com',
                                                 #    ...}

    @mock_browserid(None)
    def browserid_test():
        django_browserid.verify('random-token')  # = False
    """
    def __init__(self, email=None, audience=None):
        self.patcher = patch('django_browserid.base._verify_http_request')
        self.return_value = {
            u'audience': audience,
            u'email': email,
            u'issuer': u'browserid.org:443',
            u'status': u'okay' if email is not None else u'failure',
            u'valid-until': 1311377222765
        }

    def __enter__(self):
        self.patcher.start().return_value = self.return_value

    def __exit__(self, exc_type, exc_value, traceback):
        self.patcher.stop()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner
