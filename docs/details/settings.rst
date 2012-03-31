Settings
========

.. module:: django.conf.settings

.. data:: LOGIN_REDIRECT_URL

    **Default:** ``'/'``

    Path to redirect to on successful login.

.. data:: LOGIN_REDIRECT_URL_FAILURE

    **Default:** ``'/'``

    Path to redirect to on an unsuccessful login attempt.

.. data:: BROWSERID_CREATE_USER

    **Default:** ``True``

    If ``True`` or ``False``, enables or disables automatic user creation during
    authentication.

    If set to a string, it is treated as an import path pointing to a custom
    user creation function. See :ref:`auto-user` for more information.

.. data:: BROWSERID_VERIFIER

    **Default:** ``remote``

    Defines the PyBrowserID verifier to use. It could be one of "local",
    "remote" or "custom".

    - "local" will do the verification locally, using M2Crypto.
    - "remote" will use the verfication url (described via
      BROWSERID_VERIFICATION_URL) to check the validity of the assertion
    - "custom" let's you define a valid PyBrowserID verifier.


.. data:: BROWSERID_VERIFICATION_URL

    **Default:** ``'https://browserid.org/verify``

    Defines the URL for the BrowserID verification service to use. This is only
    useful if you are using the "remote" verifier.

.. data:: BROWSERID_DISABLE_CERT_CHECK

    **Default:** ``False``

    Disables SSL certificate verification during BrowserID verification.
    *This is for testing purposes, never disable this in production!*

.. data:: BROWSERID_CACERT_FILE

    **Default:** ``None``

    CA cert file used during validation. If none is provided, the default file
    included with requests_ is used.

.. _requests: http://docs.python-requests.org/
