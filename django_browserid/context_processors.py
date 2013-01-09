# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
from functools import partial

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe

from django_browserid.forms import (BrowserIDForm, FORM_JAVASCRIPT,
                                    BROWSERID_SHIM)


# Try to import funfactory's reverse and fall back to django's version.
try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def browserid_button(request, sign_in='Sign In', sign_out='Sign Out',
                     login_fallback='#', request_args={}):
    """
    Output the HTML for a BrowserID login button.

    :param request:
        **IGNORE:** Automatically filled in by context processor.

    :param sign_in:
        String used for the sign-in button text.

    :param sign_out:
        String used for the sign-out button text.

    :param login_fallback:
        Fallback URL to use for login with users who have JavaScript disabled.

    :param request_args:
        Dictionary of arguments to be passed to navigator.id.request for
        customizing the BrowserID login popup. Can also be a string of JSON.

        A list of valid options is available at
        https://developer.mozilla.org/en-US/docs/DOM/navigator.id.request
    """
    if isinstance(request_args, dict):
        request_args = json.dumps(request_args)
    elif isinstance(request_args, basestring):
        request_args = escape(request_args)

    return render_to_string('browserid/button.html', {
        'form': BrowserIDForm(),
        'request_args': request_args,
        'sign_in': sign_in,
        'sign_out': sign_out,
        'login_url': reverse('browserid_login'),
        'logout_url': reverse('browserid_logout')
    }, RequestContext(request))


def browserid_js(form, include_shim=True):
    """
    Returns <script> tags for the JavaScript required by the BrowserID login
    button.

    :param form:
        **IGNORE:** Automatically filled in by context processor.

    :param include_shim:
        A boolean that determines if the persona.org JavaScript shim is included
        in the output. Useful if you want to minify the button JavaScript using
        a library like django-compressor that can't handle external JavaScript.
    """
    files = FORM_JAVASCRIPT + ((BROWSERID_SHIM,) if include_shim else ())

    tags = ['<script type="text/javascript" src="{0}"></script>'
            .format(form.media.absolute_path(path)) for path in files]
    return mark_safe('\n'.join(tags))


def browserid(request):
    """A context processor that adds a BrowserID button to the request."""
    form = BrowserIDForm(auto_id=False)
    browserid_info = mark_safe("""
        <div id="browserid-info" style="display: none;" data-user-email="{0}">
        </div>
    """.format(getattr(request.user, 'email', '')))

    return {
        'browserid_form': form,  # For custom buttons.
        'browserid_info': browserid_info,
        'browserid_button': partial(browserid_button, request),
        'browserid_js': partial(browserid_js, form)
    }
