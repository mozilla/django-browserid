Contributor Setup
=================
So you want to contribute to django-browserid? Great! We really appreciate any
help you can give!

The documentation below should help you set up a development environment and
run the tests to ensure that your changes work properly.


Get the code
------------
You can check out the code from the `github repository`_:

.. code-block:: sh

    git clone git://github.com/mozilla/django-browserid.git
    cd django-browserid

It is a good idea to create a `virtualenv`_ (the example here uses
`virtualenvwrapper`_) for isolating your development environment. To create a
virtualenv and install all development packages:

.. code-block:: sh

    mkvirtualenv django-browserid
    pip install -r requirements.txt


Running tests
-------------
To check if your changes break any existing functionality, you can run the
test suite:

.. code-block:: sh

    ./setup.py test

Before submitting a pull request, you should run the test suite in all the
Django/Python combinations that we support. We support running the tests in all
these combinations via tox_:

.. code-block:: sh

    pip install tox
    tox


Documenation
------------
If you make changes to the documentation, you can build it locally with this
command:

.. code-block:: sh

    make -C docs/ html

The generated files can be found in ``docs/_build/html``.


JavaScript Tests
----------------
To run the JavaScript tests, you must have `node.js`_  installed. Then, use the
npm command to install the test dependencies:

.. code-block:: sh

    npm install

After that, you can run the JavaScript tests with the following command from
the repo root:

.. code-block:: sh

    npm test


.. _`github repository`: https://github.com/mozilla/django-browserid
.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
.. _`node.js`: https://nodejs.org/
.. _karma: https://karma-runner.github.io/
.. _`karma-mocha`: https://github.com/karma-runner/karma-mocha
.. _tox: http://tox.readthedocs.org/en/latest/
