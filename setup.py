#!/usr/bin/env python
import codecs
import os
import re
from setuptools import setup, find_packages

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts), encoding='utf8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-browserid',
    description='Django application for adding BrowserID support.',
    long_description=read('README.rst'),
    version=find_version('django_browserid/__init__.py'),
    packages=find_packages(),
    author='Paul Osman, Michael Kelly',
    author_email='mkelly@mozilla.com',
    url='https://github.com/mozilla/django-browserid',
    license='MPL v2.0',
    install_requires=['requests>=1.0.0', 'fancy_tag==0.2.0'],
    test_suite="runtests.runtests",
    include_package_data=True,
    zip_safe=False,  # because we rely on finding templates on the filesystem
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
