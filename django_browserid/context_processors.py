"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django_browserid.forms import BrowserIDForm


def browserid_form(request):
    """
    A context processor that adds a BrowserID form to the request
    """
    return {'browserid_form': BrowserIDForm()}
