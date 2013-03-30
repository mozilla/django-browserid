# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json

from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django_browserid.forms import (BROWSERID_SHIM, BrowserIDForm,
                                    FORM_JAVASCRIPT)
from django_browserid.util import static_url


# If funfactory is available, we want to use it's locale-aware reverse instead
# of Django's reverse, so we try to import funfactory's first and fallback to
# Django's if it is not found.
try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def browserid_info(request):
    """
    Output the HTML for the login form and the info tag. Should be called once
    at the top of the page just below the <body> tag.
    """
    form = BrowserIDForm(auto_id=False)
    request_args = getattr(settings, 'BROWSERID_REQUEST_ARGS', {})
    return render_to_string('browserid/info.html', {
        'email': getattr(request.user, 'email', ''),
        'login_url': reverse('browserid_login'),
        'request_args': json.dumps(request_args),
        'form': form,
    }, RequestContext(request))


def browserid_button(text=None, next=None, link_class=None,
                     attrs=None, href='#'):
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
    if isinstance(attrs, basestring):
        attrs = json.loads(attrs)

    attrs.setdefault('class', link_class)
    attrs.setdefault('href', href)
    attrs.setdefault('data-next', next)
    return render_to_string('browserid/button.html', {
        'text': text,
        'attrs': attrs,
    })


def browserid_image_link(image=None, next=None, link_class=None,
                         attrs=None, href='#'):
    """
    Output the HTML for a BrowserID image link.

    :param image:
        Image path to use inside the link.

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
    if isinstance(attrs, basestring):
        attrs = json.loads(attrs)

    attrs.setdefault('class', link_class)
    attrs.setdefault('href', href)
    attrs.setdefault('data-next', next)

    return render_to_string('browserid/image.html', {
        'attrs': attrs,
        'image': image,
    })


def browserid_login(text='Sign in', image=None, next=None,
                    link_class='browserid-login', attrs=None,
                    fallback_href='#'):
    """
    Output the HTML for a BrowserID login link.

    :param text:
        Text to use inside the link. Defaults to 'Sign in', which is not
        localized.

    :param image:
        Personal branded button image to use in place of text. Accepts the
        official Mozilla Persona image names.

        Example: 'plain_sign_in_red.png'

        Note: Prepends 'browserid/' to the image path.

    :param next:
        URL to redirect users to after they login from this link. If omitted,
        the LOGIN_REDIRECT_URL setting will be used.

    :param link_class:
        CSS class for the link. `browserid-login` will be added to this
        automatically.

    :param attrs:
        Dictionary of attributes to add to the link. Values here override those
        set by other arguments.

        If given a string, it is parsed as JSON and is expected to be an object.

    :param fallback_href:
        Value to use for the href of the link. If the user has disabled
        JavaScript, the login link will bring them to this page, which can be
        used as a non-JavaScript login fallback.
    """
    if 'browserid-login' not in link_class:
        link_class += ' browserid-login'
    next = next if next is not None else getattr(settings, 'LOGIN_REDIRECT_URL',
                                                 '/')
    if image:
        image_path = 'browserid/' + image
        html = browserid_image_link(image_path, next, link_class, attrs, fallback_href)
    else:
        html = browserid_button(text, next, link_class, attrs, fallback_href)

    return html


def browserid_logout(text='Sign out', link_class='browserid-logout',
                     attrs=None):
    """
    Output the HTML for a BrowserID logout link.

    :param text:
        Text to use inside the link. Defaults to 'Sign out', which is not
        localized.

    :param link_class:
        CSS class for the link. `browserid-logout` will be added to this
        automatically.

    :param attrs:
        Dictionary of attributes to add to the link. Values here override those
        set by other arguments.

        If given a string, it is parsed as JSON and is expected to be an object.
    """
    if 'browserid-logout' not in link_class:
        link_class += ' browserid-logout'
    return browserid_button(text, None, link_class, attrs,
                            reverse('browserid_logout'))


def browserid_js(include_shim=True):
    """
    Returns <script> tags for the JavaScript required by the BrowserID login
    button. Requires use of the staticfiles app.

    :param include_shim:
        A boolean that determines if the persona.org JavaScript shim is included
        in the output. Useful if you want to minify the button JavaScript using
        a library like django-compressor that can't handle external JavaScript.
    """
    files = [static_url(path) for path in FORM_JAVASCRIPT]
    if include_shim:
        files.append(BROWSERID_SHIM)

    tags = ['<script type="text/javascript" src="{0}"></script>'.format(path)
            for path in files]
    return mark_safe('\n'.join(tags))
