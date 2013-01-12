Settings
========

.. module:: django.conf.settings

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

.. data:: BROWSERID_CREATE_USER

    **Default:** ``True``

    If ``True`` or ``False``, enables or disables automatic user creation during
    authentication.

    If set to a string, it is treated as an import path pointing to a custom
    user creation function. See :ref:`auto-user` for more information.

.. data:: BROWSERID_VERIFICATION_URL

    **Default:** ``'https://browserid.org/verify``

    Defines the URL for the BrowserID verification service to use.

.. data:: BROWSERID_SHIM

   **Default:** 'https://login.persona.org/include.js'

   The URL to use for the BrowserID JavaScript shim.

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
