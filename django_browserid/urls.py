# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url
from django.contrib.auth.views import logout
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def _load_module_setting(name):
    path = getattr(settings, name)
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]

    try:
        mod = import_module(module)
    except ImportError:
        raise ImproperlyConfigured('Error importing %s'
                                   ' function.' % name)
    except ValueError:
        raise ImproperlyConfigured('Error importing %(name)s'
                                   ' function. Is %(name)s a'
                                   ' string?' % dict(name=name))

    try:
        return getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module {0} does not define a {1} '
                                   'function.'.format(module, attr))


if getattr(settings, 'BROWSERID_VERIFY_CLASS', None):
    Verify = _load_module_setting('BROWSERID_VERIFY_CLASS')
else:
    from django_browserid.views import Verify


urlpatterns = patterns('',
    url(r'^login/', Verify.as_view(), name='browserid_login'),
    url(r'^logout/', logout,
        {'next_page': getattr(settings, 'LOGOUT_REDIRECT_URL', '/')},
        name='browserid_logout')
)
