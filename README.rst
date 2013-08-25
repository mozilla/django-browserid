django-browserid
================

|TravisCI|_

.. |TravisCI| image:: https://secure.travis-ci.org/mozilla/django-browserid.png?branch=master
.. _TravisCI: https://secure.travis-ci.org/mozilla/django-browserid

django-browserid is a library that integrates BrowserID_ authentication into
Django_.

.. _Django: http://www.djangoproject.com/
.. _BrowserID: https://login.persona.org/

Tested Under
------------
* Python

  * 2.6
  * 2.7
  * 3.2 (experimental)
  * 3.3

* Django

  * 1.3.7
  * 1.4.5
  * 1.5.2

Documentation
-------------

http://django-browserid.rtfd.org

Need Help?
----------

First, check out the `troubleshooting`_ section of the documentation, which
covers solutions to several common problems.

If that doesn't help, questions can be sent to the #webdev channel on
irc.mozilla.org, or by email to the `current maintainer`_.

.. _troubleshooting: http://django-browserid.readthedocs.org/en/latest/details/troubleshooting.html
.. _current maintainer: mailto:mkelly@mozilla.org

Testing
-------
0. (Recommended) Create a virtualenv for django-browserid testing.
1. Install test requirements with ``pip install -r requirements.txt``
2. Run test suite with ``python setup.py test``

License
-------

This software is licensed under the `Mozilla Public License v. 2.0`_. For more
information, read the file ``LICENSE``.

.. _Mozilla Public License v. 2.0: http://mozilla.org/MPL/2.0/
