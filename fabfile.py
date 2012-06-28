"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import os

from fabric.api import local


ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ['PYTHONPATH'] = ROOT


def test():
    """Run test suite."""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_browserid.tests.settings'
    os.environ['REUSE_DB'] = '0'

    # Add tables and flush DB
    local('django-admin.py syncdb --noinput')
    local('django-admin.py flush --noinput')

    local('django-admin.py test')
