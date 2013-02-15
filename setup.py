import codecs
import os
import re
from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


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
    install_requires=['requests>=0.9.1', 'fancy_tag==0.2.0'],
    include_package_data=True,
)
