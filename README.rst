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

|TravisCI|_

.. |TravisCI| image:: https://travis-ci.org/mozilla/django-browserid.svg?branch=master
.. _TravisCI: https://travis-ci.org/mozilla/django-browserid

django-browserid is a library that integrates BrowserID_ authentication into
Django_.

Supported versions include Python 2.7, 3.2, and onward, and Django 1.7 and up.
For more details, check this project's `tox test suite`_ or TravisCI_.

.. _Django: https://www.djangoproject.com/
.. _BrowserID: https://login.persona.org/
.. _tox test suite: https://github.com/mozilla/django-browserid/blob/master/tox.ini


Documentation
-------------

http://django-browserid.readthedocs.org/


Need Help?
----------

First, check out the `troubleshooting`_ section of the documentation, which
covers solutions to several common problems.

If that doesn't help, questions can be sent to the #webdev channel on
irc.mozilla.org, or by email to the `current maintainer`_.

.. _troubleshooting: http://django-browserid.readthedocs.org/en/latest/user/troubleshooting.html
.. _current maintainer: mailto:mkelly@mozilla.org


License
-------

This software is licensed under the `Mozilla Public License v. 2.0`_. For more
information, read the file ``LICENSE``.

.. _Mozilla Public License v. 2.0: https://www.mozilla.org/MPL/2.0/
