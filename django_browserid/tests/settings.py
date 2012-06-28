TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

DATABASES = {
    'default': {
        'NAME': 'test.db',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django_nose',
    'django_browserid',

    'django.contrib.auth',
    'django.contrib.contenttypes',
)

ROOT_URLCONF = 'django_browserid.tests.urls'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
)

SITE_URL = 'http://testserver'

BROWSERID_CREATE_USER = True
BROWSERID_USERNAME_ALGO = None
