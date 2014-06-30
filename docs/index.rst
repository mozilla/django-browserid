django-browserid
================
Release v\ |version|. (:doc:`Quickstart <user/quickstart>`)

django-browserid is a Python library that integrates BrowserID_ authentication
into Django_.

BrowserID is an open, decentralized protocol for authenticating users based on
email addresses. django-browserid provides the necessary hooks to get Django
to authenticate users via BrowserID. By default, django-browserid relies on
Persona_ for the client-side JavaScript shim and for assertion verification.

django-browserid is tested on Python 2.6 to 3.3 and Django 1.4 to 1.6. See
`tox.ini`_ for more details.

django-browserid depends on:

- Requests_ >= 1.0.0
- fancy_tag_ == 0.2.0
- jQuery_ >= 1.8 (if you are using ``api.js`` and ``browserid.js``).

django-browserid is a work in progress. Contributions are welcome. Feel free
to fork_ and contribute!

.. _Django: http://www.djangoproject.com/
.. _BrowserID: https://github.com/mozilla/id-specs/blob/prod/browserid/index.md
.. _Persona: https://persona.org
.. _tox.ini: https://github.com/mozilla/django-browserid/blob/master/tox.ini
.. _Requests: http://docs.python-requests.org/
.. _fancy_tag: https://github.com/trapeze/fancy_tag
.. _jQuery: http://jquery.com/
.. _fork: https://github.com/mozilla/django-browserid


User Guide
----------
.. toctree::
   :maxdepth: 2

   user/intro
   user/quickstart
   user/customization
   user/extras
   user/settings
   user/deploying
   user/upgrading
   user/troubleshooting

API Documentation
-----------------
.. toctree::
   :maxdepth: 2

   api/python
   api/javascript

Contributor Guide
-----------------
.. toctree::
   :maxdepth: 1

   contributor/setup
   contributor/guidelines
   contributor/changelog
   contributor/authors
