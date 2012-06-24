from distutils.core import setup

setup(
    name='django-browserid',
    version='0.5.1',
    packages=['django_browserid', 'django_browserid.tests'],
    author='Paul Osman, Michael Kelly',
    author_email='mkelly@mozilla.com',
    url='https://github.com/mozilla/django-browserid',
    install_requires='requests>=0.9.1',
    package_data={'django_browserid': ['static/browserid/*.js']},
)
