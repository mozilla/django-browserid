Persona is Shutting Down
========================
Mozilla has announced that `Persona will be shutting down November 2016`_.
django-browserid `relies on the Persona service`_ and will stop functioning
properly once Persona is shut down. While it is possible to self-host Persona
and configure django-browserid to rely on your own instance, this is difficult
and not recommended. See the wiki page linked above for recommended alternatives
to Persona for authentication.

.. _Persona will be shutting down November 2016: https://wiki.mozilla.org/Identity/Persona_Shutdown_Guidelines_for_Reliers
.. _relies on the Persona service: http://django-browserid.readthedocs.org/en/latest/user/intro.html#persona-dependence


django-browserid
================
Release v\ |version|. (:doc:`Quickstart <user/quickstart>`)

django-browserid is a Python library that integrates BrowserID_ authentication
into Django_.

BrowserID is an open, decentralized protocol for authenticating users based on
email addresses. django-browserid provides the necessary hooks to get Django
to authenticate users via BrowserID. By default, django-browserid relies on
Persona_ for the client-side JavaScript shim and for assertion verification.

django-browserid is tested on Python 2.7 and 3.4 onward, and supports Django
1.8 and up. See `tox.ini`_ for more details.

django-browserid depends on:

- Requests_ >= 1.0.0
- jQuery_ >= 1.8 (if you are using ``api.js`` and ``browserid.js``).

django-browserid is a work in progress. Contributions are welcome. Feel free
to fork_ and contribute!

.. _Django: https://www.djangoproject.com/
.. _BrowserID: https://github.com/mozilla/id-specs/blob/prod/browserid/index.md
.. _Persona: https://persona.org
.. _tox.ini: https://github.com/mozilla/django-browserid/blob/master/tox.ini
.. _Requests: http://docs.python-requests.org/
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
