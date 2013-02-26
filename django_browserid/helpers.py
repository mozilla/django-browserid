# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django_browserid.forms import FORM_JAVASCRIPT, BROWSERID_SHIM


def browserid_button(text=None, next=None, link_class=None, attrs=None):
    attrs = attrs or {}
    if isinstance(attrs, basestring):
        attrs = json.loads(attrs)

    attrs.setdefault('class', link_class)
    attrs.setdefault('href', '#')
    attrs.setdefault('data-next', next)

    return render_to_string('browserid/button.html', {
        'text': text,
        'attrs': attrs,
    })


def browserid_login(text='Sign in', next=None, link_class='browserid-login',
                    attrs=None):
    """
    Output the HTML for a BrowserID login link.

    :param text:
        Text to use inside the link.

    :param next:
        URL to redirect users to after they login from this link. If omitted,
        the LOGIN_REDIRECT_URL setting will be used.

    :param link_class:
        CSS class for the link.

    :param attrs:
        Attributes for the <a> element itself. Attributes specified by this take
        precedence over those specified by other arguments.
    """
    next = next or getattr(settings, 'LOGIN_REDIRECT_URL', '/')
    return browserid_button(text, next, link_class, attrs)


def browserid_logout(text='Sign out', next=None, link_class='browserid-logout',
                    attrs=None):
    """
    Output the HTML for a BrowserID logout link.

    :param text:
        Text to use inside the link.

    :param next:
        URL to redirect users to after they logout from this link. If omitted,
        the LOGOUT_REDIRECT_URL setting will be used.

    :param link_class:
        CSS class for the link.

    :param attrs:
        Attributes for the <a> element itself. Attributes specified by this take
        precedence over those specified by other arguments.
    """
    next = next or getattr(settings, 'LOGOUT_REDIRECT_URL', '/')
    return browserid_button(text, next, link_class, attrs)


def browserid_js(include_shim=True):
    """
    Returns <script> tags for the JavaScript required by the BrowserID login
    button. Requires use of the staticfiles app.

    :param include_shim:
        A boolean that determines if the persona.org JavaScript shim is included
        in the output. Useful if you want to minify the button JavaScript using
        a library like django-compressor that can't handle external JavaScript.
    """
    from django.contrib.staticfiles.storage import staticfiles_storage

    files = [staticfiles_storage.url(path) for path in FORM_JAVASCRIPT]
    files += ((BROWSERID_SHIM,) if include_shim else ())

    tags = ['<script type="text/javascript" src="{0}"></script>'.format(path)
            for path in files]
    return mark_safe('\n'.join(tags))
