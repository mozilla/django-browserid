Troubleshooting
===============

CSP WARN: Directive "..." violated by https://browserid.org/include.js
----------------------------------------------------------------------

This warning appears in the Error Console when your site uses 
`Content Security Policy`_ without making an exception for the browserid.org
external JavaScript include.

To fix this, include https://browserid.org in your script-src directive. If 
you're using the `django-csp`_ library, the following settings will work::

    CSP_SCRIPT_SRC = ("'self'", 'https://browserid.org',)
    CSP_FRAME_SRC = ("'self'", 'https://browserid.org',)

.. note:: The example above also includes the frame-src directive. There is an
   iframe used during BrowserID login, but some people report that login will
   work without the directive. In general, you should probably include it.

.. _Content Security Policy: https://developer.mozilla.org/en/Security/CSP
.. _django-csp: https://github.com/mozilla/django-csp