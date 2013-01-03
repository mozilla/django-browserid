Setup
=====

Installation
------------

You can use pip to install django-browserid and requirements:

   pip install django-browserid


Configuration
-------------

To use ``django-browserid``, you'll need to make a few changes to your
``settings.py`` file::

    # Add 'django_browserid' to INSTALLED_APPS.
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'django_browserid',  # Load after auth
        # ...
    )

    # Add the domain and protocol you expect to use in SITE_URL.
    SITE_URL = 'https://example.com:8000'  # Note: No trailing slash

    # Add the django_browserid authentication backend.
    AUTHENTICATION_BACKENDS = (
       # ...
       'django_browserid.auth.BrowserIDBackend',
       # ...
    )

    # Add the django_browserid context processor.
    TEMPLATE_CONTEXT_PROCESSORS = (
       # ...
       'django_browserid.context_processors.browserid',
       # ...
    )

.. note:: BrowserID uses an assertion and an audience to verify the user. This
   ``SITE_URL`` is used to determine the audience. For security reasons, it is
   *very important* that you set ``SITE_URL`` correctly.

Next, edit your ``urls.py`` file and add the following::

    urlpatterns = patterns('',
        # ...
        (r'^browserid/', include('django_browserid.urls')),
        # ...
    )

You can also set the following optional settings in ``settings.py``::

    # Path to redirect to on successful login.
    LOGIN_REDIRECT_URL = '/'

    # Path to redirect to on unsuccessful login attempt.
    LOGIN_REDIRECT_URL_FAILURE = '/'

    # Path to redirect to on logout.
    LOGOUT_REDIRECT_URL = '/'

Finally, you'll need to add the login button to your templates. There are three
things you will need to add to your templates:

1. ``{{ browserid_info }}``: Invisible element that stores info about the
   current user. Must be within the ``<body>`` tag and appear only **once**.

2. ``{{ browserid_js() }}``: Outputs the ``<script>`` tags for the button
   JavaScript. Must be somewhere on the page, typically at the bottom right
   before the ``</body>`` tag to allow the page to visibly load before
   executing.

3. ``{{ browserid_button() }}``: Outputs the HTML for the login button itself.

A complete example::

    <html>
      <body>
        {{ browserid_info }}
        <header>
          <h1>My Site</h1>
          <div class="authentication">
            {{ browserid_button() }}
          </div>
        </header>
        <article>
          <p>Welcome to my site!</p>
        </article>
        {{ browserid_js() }}
      </body>
    </html>


.. note:: The JavaScript assumes you have `jQuery`_ 1.7 or higher on your site.

``browserid_button`` will display a login button if the user is logged out, and
a logout button if the user is logged in.

.. autofunction:: django_browserid.context_processors.browserid_button

.. autofunction:: django_browserid.context_processors.browserid_js

.. _jQuery: http://jquery.com/


Static Files
------------

``browserid_js`` uses `Form Media`_ and the Django `staticfiles`_ app to serve
the JavaScript for the buttons. If you don't want to use the static files
framework, you'll need to include the JavaScript manually on any page you use
the ``browserid_button`` function.

The files needed are the Persona JavaScript shim, which should be loaded from
``https://login.persona.org/include.js`` in a script tag, and
``django_browserid/static/browserid/browserid.js``, which is part of the
django-browserid library.

.. _Form Media: https://docs.djangoproject.com/en/dev/topics/forms/media/
.. _staticfiles: https://docs.djangoproject.com/en/dev/howto/static-files/


Content Security Policy
-----------------------
If your site uses `Content Security Policy`_, you will have to add directives
to allow the external persona.org JavaScript, as well as an iframe used as part
of the login process.

If you're using `django-csp`_, the following settings will work::

    CSP_SCRIPT_SRC = ("'self'", 'https://login.persona.org')
    CSP_FRAME_SRC = ("'self'", 'https://login.persona.org')

.. _Content Security Policy: https://developer.mozilla.org/en/Security/CSP
.. _django-csp: https://github.com/mozilla/django-csp
