# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured

from django_browserid import views
from django_browserid.util import import_from_setting


logger = logging.getLogger(__name__)


try:
    Verify = import_from_setting('BROWSERID_VERIFY_CLASS')
    logger.debug('django_browserid using custom Verify view ' +
                 '.'.join([Verify.__module__, Verify.__name__]))
except ImproperlyConfigured as e:
    logger.debug('django_browserid using default Verify view.')
    Verify = views.Verify


urlpatterns = [
    url(r'^browserid/login/$', Verify.as_view(), name='browserid.login'),
    url(r'^browserid/logout/$', views.Logout.as_view(), name='browserid.logout'),
    url(r'^browserid/csrf/$', views.CsrfToken.as_view(), name='browserid.csrf'),
]
