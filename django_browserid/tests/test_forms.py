# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.utils import six

from django_browserid.forms import BrowserIDForm


def test_invalid_assertion():
    form = BrowserIDForm({'assertion': six.u('\xe3')})
    assert not form.is_valid()


def test_valid_assertion():
    form = BrowserIDForm({'assertion': b'xxx'})
    assert form.is_valid()
