from setuptools import setup, find_packages


with open('README.rst') as file:
    long_description = file.read()

setup(
    name='django-browserid',
    description='Django application for adding BrowserID support.',
    long_description=long_description,
    version='0.7.1',
    packages=find_packages(),
    author='Paul Osman, Michael Kelly',
    author_email='mkelly@mozilla.com',
    url='https://github.com/mozilla/django-browserid',
    license='MPL v2.0',
    install_requires=['requests>=0.9.1', 'fancy_tag==0.2.0'],
    include_package_data=True,
)
