# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.utils.functional import Promise
from django.utils.encoding import force_unicode


class LazyEncoder(json.JSONEncoder):
    """
    JSONEncoder that turns Promises into unicode strings to support functions
    like ugettext_lazy and reverse_lazy.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)


# Attempt to use staticfiles_storage.url to retrieve static file URLs.
# If it can't be found (Django 1.3), default to prepending settings.STATIC_URL
# to the given path.
try:
    from django.contrib.staticfiles.storage import staticfiles_storage
    static_url = staticfiles_storage.url
except ImportError:
    from django.conf import settings

    def static_url(path):
        """Return a public URL for the given static file path."""
        return ''.join([settings.STATIC_URL, path])

