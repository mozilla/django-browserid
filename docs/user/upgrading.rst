Upgrading
=========
If you're looking to upgrade from an older version of django-browserid, you're
in the right place. This document describes the major changes required to get
your site up to the latest and greatest!


0.10.1 to 0.11.1
---------------
No changes are necessary to switch from 0.10.1 to 0.11.1.


0.9 to 0.10.1
-------------
- The minimum supported version of requests is now 1.0.0, and six has been
  removed from the requirements.

- Replace the ``SITE_URL`` setting with ``BROWSERID_AUDIENCES``, which is
  essentially the same setting, but must be a list of strings (wrapping your
  old ``SITE_URL`` value with square brackets to make it a list is fine):

  .. code-block:: python

      BROWSERID_AUDIENCES = ['https://www.example.com']

  - On local development installs, you can remove ``SITE_URL`` entirely, as
    ``BROWSERID_AUDIENCES`` isn't required when ``DEBUG`` is True.

- In your root urlconf, remove any regex in front of the include for
  django-browserid urls. Because the new JavaScript relies on views being
  available at certain URLs, you must not change the path that the
  django-browserid views are served:

  .. code-block:: python

      urlpatterns = patterns('',
          # ...
          (r'', include('django_browserid.urls')),
          # ...
      )

- Remove ``django_browserid.context_processors.browserid`` from your
  ``TEMPLATE_CONTEXT_PROCESSORS`` setting, as the context processor no longer
  exists.

- ``browserid.js`` has been split into ``api.js``, which contains just the
  JavaScript API, and ``browserid.js``, which contains the sample code for
  hooking up login buttons. If you aren't using the ``browserid_js`` helper to
  include the JavaScript on the page, you probably need to update your project
  to either include both or just ``api.js``.

- The included JavaScript requires jQuery 1.8 or higher instead of jQuery 1.7.


0.8 to 0.9
----------
- Six v1.3 or higher is now required.


0.7.1 to 0.8
------------
- fancy_tag 0.2.0 has been added to the required libraries.

- Rename the ``browserid_form`` context processor to ``browserid`` in the
  ``TEMPLATE_CONTEXT_PROCESSORS`` setting:

  .. code-block:: python

      TEMPLATE_CONTEXT_PROCESSORS = (
          # ...
          'django_browserid.context_processors.browserid',
          # ...
      )

- Replace custom login button code with the new template helpers,
  ``browserid_info``, ``browserid_login``, and ``browserid_logout``.

  - ``browserid_info`` should be added just below ``<body>`` on any page that
    includes a login button.

  - ``browserid_login`` and ``browserid_logout`` output login and logout links
    respectively.

- It's now recommended to include the JavaScript for the login buttons using
  the ``browserid_js`` helper, which outputs the appropriate ``<script>`` tags.

- The included JavaScript requires jQuery 1.7 or higher instead of jQuery 1.6.
