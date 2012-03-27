from distutils.core import setup

setup(
    name='django-browserid',
    version='0.2',
    packages=['django_browserid'],
    author="Paul Osman",
    author_email="paul@mozillafoundation.org",
    install_requires="requests==0.9.1",
    package_data={"django_browserid": ["static/browserid/*.js"]},
)
