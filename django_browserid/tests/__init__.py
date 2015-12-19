# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.test import TestCase as DjangoTestCase
from django.utils.encoding import smart_text
from django.utils.functional import wraps

from mock import patch

from django_browserid.auth import BrowserIDBackend
from django_browserid.base import MockVerifier


def fake_create_user(email):
    pass


class mock_browserid(object):
    """
    Mock verification in :class:`django_browserid.auth.BrowserIDBackend`.

    Can be used as a context manager or as a decorator:

    with mock_browserid('a@b.com'):
        django_browserid.verify('random-token')  # = {'status': 'okay',
                                                 #    'email': 'a@b.com',
                                                 #    ...}

    @mock_browserid(None)
    def browserid_test():
        django_browserid.verify('random-token')  # = False
    """
    def __init__(self, email, **kwargs):
        """
        :param email:
            Email to return in the verification result. If None, the verification will fail.

        :param kwargs:
            Keyword arguments are passed on to :class:`django_browserid.base.MockVerifier`, which
            updates the verification result with them.
        """
        self.patcher = patch.object(BrowserIDBackend, 'get_verifier')
        self.return_value = MockVerifier(email, **kwargs)

    def __enter__(self):
        mock = self.patcher.start()
        mock.return_value = self.return_value
        return mock

    def __exit__(self, exc_type, exc_value, traceback):
        self.patcher.stop()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner


class TestCase(DjangoTestCase):
    def assert_json_equals(self, json_str, value):
        return self.assertEqual(json.loads(smart_text(json_str)), value)

    def shortDescription(self):
        # Stop nose using the test docstring and instead the test method
        # name.
        pass


class JSON_STRING(object):
    """
    Test object that is considered equal to any string that, when
    decoded as JSON, is equal to the value passed in the constructor.

    Useful for testing against JSON strings with dicts where the key
    ordering doesn't matter.
    """
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return json.loads(other) == self.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<JSON_STRING {0}>'.format(self.value)
