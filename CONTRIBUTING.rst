Contributing Guidelines
=======================
In order to make our review/development process easier, we have some guidelines
to help you figure out how to contribute to django-browserid.


Reporting Issues
----------------
We use `Github Issues`_ to track issues and bugs for django-browserid.

.. _Github Issues: https://github.com/mozilla/django-browserid/issues


Development Guidelines
----------------------
- Python code should be covered by unit tests. JavaScript code for the
  JavaScript API should be covered by unit tests. We don't yet have tests for
  non-API JavaScript code, so manual testing is recommended currently.

- Python code should follow Mozilla's `general Webdev guidelines`_. The same
  goes for our `JavaScript guidelines`_ and `CSS guidelines`_.

  - As allowed by PEP8, we use 99-characters-per-line for Python code and
    72-characters-per-line for documentation/comments. Feel free to break these
    guidelines for readability if necessary.

.. _general Webdev guidelines: http://mozweb.readthedocs.org/en/latest/reference/python-style.html
.. _JavaScript guidelines: http://mozweb.readthedocs.org/en/latest/reference/js-style.html
.. _CSS guidelines: http://mozweb.readthedocs.org/en/latest/reference/css-style.html


Submitting a Pull Request
-------------------------
When submitting a pull request, make sure to do the following:

- Check that the Python and JavaScript tests pass in all environments. Running
  the Python tests in all environments is easy using tox_:

  .. code-block:: sh

     $ pip install tox
     $ tox

  Running the JavaScript tests requires `node.js`_. To install the test
  dependencies and run the test suite:

  .. code-block:: sh

     $ npm install
     $ npm test

- Make sure to include new tests or update existing tests to cover your
  changes.

- If you haven't, add your name, username, or alias to the ``AUTHORS.rst`` file
  as a contributor.

.. _tox: http://tox.readthedocs.org/en/latest/
.. _`node.js`: https://nodejs.org/


Additional Resources
--------------------
- IRC: #webdev on `irc.mozilla.org`_.

- Mailing list: `dev-webdev@lists.mozilla.org`_.

.. _irc.mozilla.org: https://wiki.mozilla.org/IRC
.. _dev-webdev@lists.mozilla.org: https://lists.mozilla.org/listinfo/dev-webdev
