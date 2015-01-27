# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Imports that vary depending on available libraries or python versions."""


# If funfactory is available, we want to use its locale-aware reverse
# instead of Django's reverse, so we try to import funfactory's first
# and fallback to Django's if it is not found.
try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


# If PyBrowserID is installed, we can support local verification.
try:
    import browserid
    pybrowserid_found = True
except ImportError:
    pybrowserid_found = False
