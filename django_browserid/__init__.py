"""
django-browserid

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
__version__ = '2.0.2'

from django_browserid.auth import (
    BrowserIDBackend,
    LocalBrowserIDBackend
)  # NOQA
from django_browserid.base import (
    BrowserIDException,
    get_audience,
    MockVerifier,
    RemoteVerifier,
    LocalVerifier,
    VerificationResult
)  # NOQA
