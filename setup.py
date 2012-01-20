from setuptools import setup

import django_browserid


setup(
    name='django-browserid',
    version=django_browserid.__version__,
    packages=['django_browserid'],
    author="Paul Osman",
    author_email="paul@mozillafoundation.org",
    install_requires="requests==0.9.1"
)
