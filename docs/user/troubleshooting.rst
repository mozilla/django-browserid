Troubleshooting
===============
If you are having trouble getting django-browserid to work properly, try
reading through the sections below for help on dealing with common issues.


Logging Errors
--------------
Before you do anything else, check to see if django-browserid is logging issues
by setting up a logger for ``django_browserid`` in your logging config. Here's
a sample config that will log messages from django-browserid to the console:

.. code-block:: python

    LOGGING = {
       'version': 1,
       'handlers': {
           'console':{
               'level': 'DEBUG',
               'class': 'logging.StreamHandler'
           },
       },
       'loggers': {
           'django_browserid': {
               'handlers': ['console'],
               'level': 'DEBUG',
           }
       },
    }


If you recently updated...
--------------------------
If you are hitting problems after updating django-browserid, check to make sure
your installed copy matches the tagged version on Github. In particular,
leftover ``*.pyc`` files may cause unintended side effects. This is common when
installing without using a package manager like ``pip``.


Nothing happens when clicking the login button
----------------------------------------------
If nothing happens when you click the login button on your website, check that
you've included ``api.js`` and ``browserid.js`` on your webpage:

.. code-block:: html+django

    <script src="{% static 'browserid/api.js' %}"></script>
    <script src="{% static 'browserid/browserid.js' %}"></script>


CSP WARN: Directive "..." violated by https://browserid.org/include.js
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You may see this warning in your browser's error console when your site uses
`Content Security Policy`_ without making an exception for the persona.org
external JavaScript include.

To fix this, include https://login.persona.org in your script-src and frame-src
directive. If you're using the `django-csp`_ library, the following settings
will work::

    CSP_SCRIPT_SRC = ("'self'", 'https://login.persona.org')
    CSP_FRAME_SRC = ("'self'", 'https://login.persona.org')

.. _Content Security Policy: https://developer.mozilla.org/en/Security/CSP
.. _django-csp: https://github.com/mozilla/django-csp


Login fails silently after the Persona popup closes
---------------------------------------------------
There are a few reasons why login may fail without an error message after the
Persona popup closes:

SESSION_COOKIE_SECURE is False
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`SESSION_COOKIE_SECURE` controls if the `secure` flag is set on the session
cookie. If set to True for site running in an environment that doesn't use
HTTPS, the session cookie won't be sent by your browser because you're using an
HTTP connection.

The solution is to set `SESSION_COOKIE_SECURE` to False on your local instance
in your settings file:

.. code-block:: python

    SESSION_COOKIE_SECURE = False

No cache configured
~~~~~~~~~~~~~~~~~~~
Several projects (especially projects based on playdoh_, which uses
`django-session-csrf`_) store session info in the cache rather than the
database, and if your local instance has no cache configured, the session
information will not be stored and login will fail silently.

To solve this issue, you should configure your local instance to use an
in-memory cache with the following in your local settings file::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }

.. _playdoh: https://github.com/mozilla/playdoh
.. _django-session-csrf: https://github.com/mozilla/django-session-csrf


Login fails with an error message on a valid account
----------------------------------------------------
If you see a login error page after attempting to login, but you know that
your Persona account is valid and should be able to login, check for these
issues:

Your website uses HTTPS but django-browserid thinks it's using HTTP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are using django-browserid behind a load balancer that uses HTTP
internally for your SSL connections, you may experience failed logins. The
``request.is_secure()`` method determines if a request is using HTTPS by
checking for the header specified by the `SECURE_PROXY_SSL_HEADER`_ setting. If
this is unset or the header is missing, Django assumes the request uses HTTP.

Because the audiences stored in
:attr:`BROWSERID_AUDIENCES <django.conf.settings.BROWSERID_AUDIENCES>` include
the protocol used to access the site, you may get an error when
django-browserid checks the audiences against the URL from the request due to
the request thinking it's not using SSL when it is.

Make sure that ``SECURE_PROXY_SSL_HEADER`` is set to an appropriate value for
your load balancer. An example configuration using nginx_ might look like this:

.. code-block:: python

    # settings.py
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

.. code-block:: nginx

    # nginx config
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Protocol https; # Tell django we're using https
    }

.. _SECURE_PROXY_SSL_HEADER: https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
.. _nginx: http://wiki.nginx.org/


Still having issues? Ask for help!
----------------------------------
If your issue isn't listed above and you're having trouble tracking it down,
you can try asking for help from:

- The #webdev channel on `irc.mozilla.org`_,
- The `dev-webdev@lists.mozilla.org`_ mailing list,
- or by emailing :doc:`the maintainers </contributor/authors>` directly.

.. _irc.mozilla.org: http://irc.mozilla.org
.. _dev-webdev@lists.mozilla.org: https://lists.mozilla.org/listinfo/dev-webdev
