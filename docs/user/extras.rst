Extras
======
django-browserid comes with a few extra pieces to make development easier.
They're documented below.


.. _offline-development:

Offline Development
-------------------
Because django-browsered :ref:`relies on the Persona service
<persona-dependence>`, offline development is not supported by default.
To work around this, django-browserid includes an auto-login system that lets
you specify an email to log the user in with when they click a login button.

.. warning:: Auto-login is a huge security hole as it bypasses authentication.
             Only use it for local development on your own computer; **never**
             use it on a publicly-visible machine or your live, production
             website.


Enable auto-login
~~~~~~~~~~~~~~~~~

To enable auto-login:

1. Add the ``AutoLoginBackend`` class to the ``AUTHENTICATION_BACKENDS`` setting.
2. Set :attr:`BROWSERID_AUTOLOGIN_EMAIL <django.conf.settings.BROWSERID_AUTOLOGIN_EMAIL>`
   to the email you want to be logged in as.
3. Set :attr:`BROWSERID_AUTOLOGIN_ENABLED <django.conf.settings.BROWSERID_AUTOLOGIN_ENABLED>`
   to ``True``.
4. If you are not using
   :py:func:`browserid_js template helper <django_browserid.helpers.browserid_js>`,
   you have to manually add ``browserid/autologin.js`` to your site.

For example:

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
       'django_browserid.auth.AutoLoginBackend',
       'django_browserid.auth.BrowserIDBackend',  # After auto-login.
    )

    BROWSERID_AUTOLOGIN_EMAIL = 'bob@example.com'
    BROWSERID_AUTOLOGIN_ENABLED = True

Once these are set, any login button that uses the :doc:`JavaScript API
</api/javascript>` will not attempt to show the Persona popup, and will
immediately log you in with the email you set above.


Disable auto-login
~~~~~~~~~~~~~~~~~~

To disable auto-login:

1. Set :attr:`BROWSERID_AUTOLOGIN_ENABLED <django.conf.settings.BROWSERID_AUTOLOGIN_ENABLED>`
   to ``False``.
2. If you added ``browserid/autologin.js`` to your site, you must remove it.
