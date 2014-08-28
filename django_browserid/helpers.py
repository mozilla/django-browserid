# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.six import string_types

from django_browserid.compat import jingo_register, reverse
from django_browserid.util import LazyEncoder

MANDATORY_LINK_CLASS_LOGIN = 'browserid-login'
DEFAULT_LINK_CLASS_LOGIN = MANDATORY_LINK_CLASS_LOGIN + ' persona-button'
MANDATORY_LINK_CLASS_LOGOUT = 'browserid-logout'
DEFAULT_LINK_CLASS_LOGOUT = MANDATORY_LINK_CLASS_LOGOUT


@jingo_register.function
def browserid_info():
    """
    Output the HTML for the info tag, which contains the arguments for
    navigator.id.request from the BROWSERID_REQUEST_ARGS setting. Should
    be called once at the top of the page just below the <body> tag.
    """
    # Force request_args to be a dictionary, in case it is lazily generated.
    request_args = dict(getattr(settings, 'BROWSERID_REQUEST_ARGS', {}))

    info = json.dumps({
        'loginUrl': reverse('browserid.login'),
        'logoutUrl': reverse('browserid.logout'),
        'csrfUrl': reverse('browserid.csrf'),
        'requestArgs': request_args,
    }, cls=LazyEncoder)

    return render_to_string('browserid/info.html', {
        'info': info,
    })


def browserid_button(text=None, next=None, link_class=None, attrs=None, href='#'):
    """
    Output the HTML for a BrowserID link.

    :param text:
        Text to use inside the link.

    :param next:
        Value to use for the data-next attribute on the link.

    :param link_class:
        Class to use for the link.

    :param attrs:
        Dictionary of attributes to add to the link. Values here override those
        set by other arguments.

        If given a string, it is parsed as JSON and is expected to be an object.

    :param href:
        href to use for the link.
    """
    attrs = attrs or {}
    if isinstance(attrs, string_types):
        attrs = json.loads(attrs)

    attrs.setdefault('class', link_class)
    attrs.setdefault('href', href)
    attrs.setdefault('data-next', next)
    return render_to_string('browserid/button.html', {
        'text': text,
        'attrs': attrs,
    })


@jingo_register.function
def browserid_login(text='Sign in', color=None, next=None,
                    link_class=DEFAULT_LINK_CLASS_LOGIN,
                    attrs=None, fallback_href='#'):
    """
    Output the HTML for a BrowserID login link.

    :param text:
        Text to use inside the link. Defaults to 'Sign in', which is not
        localized.

    :param color:
        Color to use for the login button; this will only work if you have
        included the default CSS provided by
        :py:func:`django_browserid.helpers.browserid_css`.

        Supported colors are: `'dark'`, `'blue'`, and `'orange'`.

    :param next:
        URL to redirect users to after they login from this link. If omitted,
        the LOGIN_REDIRECT_URL setting will be used.

    :param link_class:
        CSS class for the link. Defaults to `browserid-login persona-button`.

    :param attrs:
        Dictionary of attributes to add to the link. Values here override those
        set by other arguments.

        If given a string, it is parsed as JSON and is expected to be an object.

    :param fallback_href:
        Value to use for the href of the link. If the user has disabled
        JavaScript, the login link will bring them to this page, which can be
        used as a non-JavaScript login fallback.
    """
    if MANDATORY_LINK_CLASS_LOGIN not in link_class.split(' '):
        link_class += ' ' + MANDATORY_LINK_CLASS_LOGIN

    if color:
        if 'persona-button' not in link_class.split(' '):
            link_class += ' persona-button {0}'.format(color)
        else:
            link_class += ' ' + color

    next = next or getattr(settings, 'LOGIN_REDIRECT_URL', '/')
    return browserid_button(text, next, link_class, attrs, fallback_href)


@jingo_register.function
def browserid_logout(text='Sign out', next=None,
                     link_class=DEFAULT_LINK_CLASS_LOGOUT, attrs=None):
    """
    Output the HTML for a BrowserID logout link.

    :param text:
        Text to use inside the link. Defaults to 'Sign out', which is not
        localized.

    :param link_class:
        CSS classes for the link. The classes will be appended to the
        default class `browserid-logout`.

    :param attrs:
        Dictionary of attributes to add to the link. Values here override those
        set by other arguments.

        If given a string, it is parsed as JSON and is expected to be an object.
    """
    next = next or getattr(settings, 'LOGOUT_REDIRECT_URL', '/')

    if MANDATORY_LINK_CLASS_LOGOUT not in link_class.split(' '):
        link_class += ' ' + MANDATORY_LINK_CLASS_LOGOUT

    return browserid_button(text, next, link_class,
                            attrs, reverse('browserid.logout'))


@jingo_register.function
def browserid_js(include_shim=True):
    """
    Return <script> tags for the JavaScript required by the BrowserID login
    button. Requires use of the staticfiles app.

    If the BROWSERID_AUTOLOGIN_ENABLED setting is True, an extra JavaScript
    file for mocking out Persona will be included, and the shim won't
    be included regardless of the value of the ``include_shim`` setting.

    :param include_shim:
        A boolean that determines if the persona.org JavaScript shim is included
        in the output. Useful if you want to minify the button JavaScript using
        a library like django-compressor that can't handle external JavaScript.
    """
    files = []
    autologin_enabled = getattr(settings, 'BROWSERID_AUTOLOGIN_ENABLED', False)

    # Include navigator.id shim only if we're not doing autologin.
    if include_shim and not autologin_enabled:
        files.append(getattr(settings, 'BROWSERID_SHIM', 'https://login.persona.org/include.js'))

    # Include django-browserid API
    files.append(staticfiles_storage.url('browserid/api.js'))

    # If we're doing autologin, include the JS to mock out certain parts
    # of the API.
    if autologin_enabled:
        files.append(staticfiles_storage.url('browserid/autologin.js'))

    # Include the JS to bind to login buttons.
    files.append(staticfiles_storage.url('browserid/browserid.js'))

    tags = ['<script type="text/javascript" src="{0}"></script>'.format(path)
            for path in files]
    return mark_safe('\n'.join(tags))


@jingo_register.function
def browserid_css():
    """
    Return <link> tag for the optional CSS included with django-browserid.
    Requires use of the staticfiles app.
    """
    url = staticfiles_storage.url('browserid/persona-buttons.css')
    return mark_safe('<link rel="stylesheet" href="{0}" />'.format(url))
