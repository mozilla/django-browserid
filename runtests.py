import os
import sys

import django
from django.test.utils import get_runner
from django.conf import settings


def runtests():
    test_dir = os.path.join(os.path.dirname(__file__), 'django_browserid/tests')
    sys.path.insert(0, test_dir)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    os.environ['REUSE_DB'] = '0'
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(interactive=False, failfast=False)
    failures = test_runner.run_tests(['django_browserid.tests'])

    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()
