Deploying in Production
=======================
Deploying django-browserid in a production environment requires a few extra
changes from the setup described in the :doc:`Quickstart </user/quickstart>`:

- The :attr:`BROWSERID_AUDIENCES <django.conf.settings.BROWSERID_AUDIENCES>`
  setting is required when ``DEBUG`` is set to False. Ensure that all the
  domains that users will access your site from are listed in this setting.

- `Optional`: It is a good idea to minify the static JS and CSS files you're
  using. `django-compressor`_ and `jingo-minify`_ are examples of libraries
  you can use for minification.

.. _django-compressor: http://django-compressor.readthedocs.org/en/latest/
.. _jingo-minify: https://github.com/jsocol/jingo-minify
