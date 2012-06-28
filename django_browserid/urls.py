"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django.conf.urls.defaults import patterns, url

from django_browserid.views import Verify


urlpatterns = patterns('',
    url('^browserid/verify/', Verify.as_view(),
        name='browserid_verify')
)
