Settings
========

.. module:: django.conf.settings


Core Settings
-------------

.. data:: SITE_URL

   **Default:** No default

   Domain and protocol used to access your site. BrowserID uses this value to
   determine if an assertion was meant for your site.

   Can be a string or an iterable of strings.

   Note that this does not have to be a publicly accessible URL, so local URLs
   like ``localhost:8000`` or ``127.0.0.1`` are acceptable as long as they match
   what you are using to access your site.


Redirect URLs
-------------

.. data:: LOGIN_REDIRECT_URL

    **Default:** ``'/accounts/profile'``

    Path to redirect to on successful login. If you don't specify this, the
    default_ Django value will be used.

.. data:: LOGIN_REDIRECT_URL_FAILURE

    **Default:** ``'/'``

    Path to redirect to on an unsuccessful login attempt.

.. data:: LOGOUT_REDIRECT_URL

   **Default:** ``'/'``

   Path to redirect to on logout.


Customizing the Login Popup
---------------------------

.. data:: BROWSERID_REQUEST_ARGS

   **Default:** ``{}``

   Controls the arguments passed to ``navigator.id.request``, which are used to
   customize the login popup box. To see a list of valid keys and what they do,
   check out the `navigator.id.request documentation`_.

   .. _navigator.id.request documentation: https://developer.mozilla.org/en-US/docs/DOM/navigator.id.request


Customizing the Verify View
---------------------------

.. data:: BROWSERID_CREATE_USER

    **Default:** ``True``

    If ``True`` or ``False``, enables or disables automatic user creation during
    authentication.

    If set to a string, it is treated as an import path pointing to a custom
    user creation function. See :ref:`auto-user` for more information.

.. data:: BROWSERID_DISABLE_SANITY_CHECKS

    **Default:** False

    Controls whether the ``Verify`` view performs some helpful checks for common
    mistakes. Useful if you're getting warnings for things you know aren't
    errors.


Using a Different Identity Provider
-----------------------------------

.. data:: BROWSERID_VERIFICATION_URL

    **Default:** ``'https://browserid.org/verify``

    Defines the URL for the BrowserID verification service to use.

.. data:: BROWSERID_SHIM

   **Default:** 'https://login.persona.org/include.js'

   The URL to use for the BrowserID JavaScript shim.


Customizing Verification
------------------------

.. data:: BROWSERID_DISABLE_CERT_CHECK

    **Default:** ``False``

    Disables SSL certificate verification during BrowserID verification.
    *Never disable this in production!*

.. data:: BROWSERID_CACERT_FILE

    **Default:** ``None``

    CA cert file used during validation. If none is provided, the default file
    included with requests_ is used.

.. _requests: http://docs.python-requests.org/

.. _default: https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
