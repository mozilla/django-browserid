Settings
========
.. currentmodule:: django.conf.settings

This document describes the Django settings that can be used to customize the
behavior of django-browserid.


Core Settings
-------------
.. attribute:: BROWSERID_AUDIENCES

   :default: No default

   List of audiences that your site accepts. An audience is the protocol,
   domain name, and (optionally) port that users access your site from. This
   list is used to determine the audience a user is part of (how they are
   accessing your site), which is used during verification to ensure that the
   assertion given to you by the user was intended for your site.

   Without this, other sites that the user has authenticated with via Persona
   could use their assertions to impersonate the user on your site.

   Note that this does not have to be a publicly accessible URL, so local URLs
   like ``http://localhost:8000`` or ``http://127.0.0.1`` are acceptable as
   long as they match what you are using to access your site.


Redirect URLs
-------------
.. note:: If you want to use named URLs instead of directly including URLs into
   your settings file, you can use `reverse_lazy`_ to do so.

.. attribute:: LOGIN_REDIRECT_URL

    :default: ``'/accounts/profile'``

    Path to redirect to on successful login. If you don't specify this, the
    default Django value will be used.

.. attribute:: LOGIN_REDIRECT_URL_FAILURE

    :default: ``'/'``

    Path to redirect to on an unsuccessful login attempt.

.. attribute:: LOGOUT_REDIRECT_URL

   :default: ``'/'``

   Path to redirect to on logout.

.. _reverse_lazy: https://docs.djangoproject.com/en/dev/ref/urlresolvers/#reverse-lazy


Customizing the Login Popup
---------------------------
.. attribute:: BROWSERID_REQUEST_ARGS

   :default: ``{}``

   Controls the arguments passed to ``navigator.id.request``, which are used to
   customize the login popup box. To see a list of valid keys and what they do,
   check out the `navigator.id.request documentation`_.

   .. _navigator.id.request documentation: https://developer.mozilla.org/en-US/docs/DOM/navigator.id.request


Customizing the Verify View
---------------------------
.. attribute:: BROWSERID_VERIFY_CLASS

    :default: ``django_browserid.views.Verify``

    Allows you to substitute a custom class-based view for verifying assertions.
    For example, the string 'myapp.users.views.Verify' would import `Verify`
    from `myapp.users.views` and use it in place of the default view.

    When using a custom view, it is generally a good idea to subclass the
    default Verify and override the methods you want to change.

.. attribute:: BROWSERID_CREATE_USER

    :default: ``True``

    If ``True`` or ``False``, enables or disables automatic user creation during
    authentication. If set to a string, it is treated as an import path
    pointing to a custom user creation function.

.. attribute:: BROWSERID_DISABLE_SANITY_CHECKS

    :default: False

    Controls whether the ``Verify`` view performs some helpful checks for common
    mistakes. Useful if you're getting warnings for things you know aren't
    errors.


Using a Different Identity Provider
-----------------------------------
.. attribute:: BROWSERID_SHIM

   :default: 'https://login.persona.org/include.js'

   The URL to use for the BrowserID JavaScript shim.


Extras
------
.. attribute:: BROWSERID_AUTOLOGIN_ENABLED

   :default: ``False``

   If ``True``, enables auto-login. You must also set the auto-login email and
   authentication backend for auto-login to function. See the documentation on
   :ref:`offline development <offline-development>` for more info.

.. attribute:: BROWSERID_AUTOLOGIN_EMAIL

   :default: Not set

   The email to log users in as when auto-login is enabled. See the
   documentation on :ref:`offline development <offline-development>` for more
   info.
