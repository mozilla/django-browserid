django-browserid
================

django-browserid is a library that integrates BrowserID_ authentication into
Django_.

django-browserid provides an authentication backend, ``BrowserIDBackend``, that
verifies BrowserID assertions using different methods and authenticate users.
The verification can be done using the browserid.org verification service or
locally.

It also provides a ``verify`` function which lets you build more complex
authentication systems based on BrowserID.

django-browserid is a work in progress. Contributions are welcome. Feel free
to fork_ and contribute!

.. _Django: http://www.djangoproject.com/
.. _BrowserID: https://browserid.org/
.. _fork: https://github.com/mozilla/django-browserid

.. toctree::
   :maxdepth: 2

   setup
   details/customization
   details/settings
