# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.conf import settings
from django.template.loader import render_to_string

from django_browserid.forms import BrowserIDForm
from django_browserid.helpers import (browserid_js, browserid_login,
                                      browserid_logout)


# If funfactory is available, we want to use it's locale-aware reverse instead
# of Django's reverse, so we try to import funfactory's first and fallback to
# Django's if it is not found.
try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def browserid(request):
    """
    Context processor that adds django-browserid helpers to the template
    context.
    """
    form = BrowserIDForm(auto_id=False)
    request_args = getattr(settings, 'BROWSERID_REQUEST_ARGS', {})
    browserid_info = render_to_string('browserid/info.html', {
        'email': getattr(request.user, 'email', ''),
        'login_url': reverse('browserid_login'),
        'request_args': json.dumps(request_args),
        'form': form,
    })

    return {
        'browserid_form': form,  # For custom buttons.
        'browserid_info': browserid_info,
        'browserid_login': browserid_login,
        'browserid_logout': browserid_logout,
        'browserid_js': browserid_js
    }
