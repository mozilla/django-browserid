from distutils.core import setup

setup(
    name='django-browserid',
    description='Django application for adding BrowserID support.',
    version='0.6',
    packages=['django_browserid', 'django_browserid.tests'],
    author='Paul Osman, Michael Kelly',
    author_email='mkelly@mozilla.com',
    url='https://github.com/mozilla/django-browserid',
    license=open("LICENSE").read(),
    install_requires='requests>=0.9.1',
    package_data={'django_browserid': ['static/browserid/*.js']},
)
