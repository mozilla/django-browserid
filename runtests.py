# This file mainly exists to allow python setup.py test to work.
# http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['REUSE_DB'] = '0'

test_dir = os.path.join(os.path.dirname(__file__), 'django_browserid/tests')
sys.path.insert(0, test_dir)

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command


def runtests():
    call_command('syncdb', interactive=False)
    call_command('flush', interactive=False)
    test_runner = get_runner(settings)
    failures = test_runner(interactive=False, failfast=False).run_tests([])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
