import json

from nose.tools import eq_

from django.test import TestCase
from django.utils.functional import lazy

from django_browserid.util import LazyEncoder


def _lazy_string():
    return 'blah'
lazy_string = lazy(_lazy_string, unicode)()


class TestLazyEncoder(TestCase):
    def test_lazy(self):
        thing = ['foo', lazy_string]
        thing_json = json.dumps(thing, cls=LazyEncoder)
        eq_('["foo", "blah"]', thing_json)
