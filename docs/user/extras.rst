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

To enable auto-login, add the ``AutoLoginBackend`` class to the
``AUTHENTICATION_BACKENDS`` setting, set :attr:`BROWSERID_AUTOLOGIN_EMAIL
<django.conf.settings.BROWSERID_AUTOLOGIN_EMAIL>` to the email you want to be
logged in as, and set :attr:`BROWSERID_AUTOLOGIN_ENABLED
<django.conf.settings.BROWSERID_AUTOLOGIN_ENABLED> to ``True``.

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

.. note:: Auto-login depends on some modifications to the JavaScript that
          happen in ``browserid/autologin.js``. If you are using
          :py:func:`django_browserid.helpers.browserid_js` to include the
          JavaScript on your site, it will automatically include it and remove
          the Persona shim. If you aren't, you will have to manually add
          ``browserid/autologin.js`` to your site when you want to use
          auto-login.

.. note:: Auto-login is *only* enabled if ``BROWSERID_AUTOLOGIN_ENABLED`` is
          set to True. Even if the other settings are present,
          ``BROWSERID_AUTOLOGIN_ENABLED`` must be True for auto-login to
          function.

.. warning:: Auto-login is a huge security hole as it bypasses authentication.
             Only use it for local development on your own computer; **never**
             use it on a publicly-visible machine or your live, production
             website.
