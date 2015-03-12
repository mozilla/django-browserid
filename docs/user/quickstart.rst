Quickstart
==========
Follow these instructions to get set up with a basic install of
django-browserid:

Installation
------------
You can use pip to install django-browserid and requirements:

.. code-block:: sh

    $ pip install django-browserid


Configuration
-------------
After installation, you'll need to configure your site to use django-browserid.
Start by making the following changes to your ``settings.py`` file:

.. code-block:: python

    # Add 'django_browserid' to INSTALLED_APPS.
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'django_browserid',  # Load after auth
        # ...
    )

    # Add the django_browserid authentication backend.
    AUTHENTICATION_BACKENDS = (
       # ...
       'django.contrib.auth.backends.ModelBackend',
       'django_browserid.auth.BrowserIDBackend',
       # ...
    )

Next, edit your ``urls.py`` file and add the following:

.. code-block:: python

    urlpatterns = patterns('',
        # ...
        (r'', include('django_browserid.urls')),
        # ...
    )

.. note:: The django-browserid urlconf *must not* have a regex with the
   include. Use a blank string, as shown above.

Finally, you'll need to add the login button and info tag to your Django
templates, along with the CSS and JS files necessary to make it work:

.. code-block:: html+django

    {% load browserid %}
    <html>
      <head>
        {% browserid_css %}
      </head>
      <body>
        {% browserid_info %}
        {% if user.is_authenticated %}
          <p>Current user: {{ user.email }}</p>
          {% browserid_logout text='Logout' %}
        {% else %}
          {% browserid_login text='Login' color='dark' %}
        {% endif %}

        <script src="https://code.jquery.com/jquery-1.9.1.min.js"></script>
        {% browserid_js %}
      </body>
    </html>

.. note:: ``api.js`` and ``browserid.js`` require `jQuery`_ 1.8 or higher.

.. note:: The ``browserid_info`` tag is required on any page that users can log
   in from. It's recommended to put it just below the ``<body>`` tag.

And that's it! You can now log into your site using Persona!

Once you're ready, you should check out :doc:`how to customize django-browserid
</user/customization>` to your liking.

.. _jQuery: http://jquery.com/


Note for Jinja2 / Jingo Users
-----------------------------
If you're using Jinja2_ via jingo_, here's a version of the example above
written in Jinja2:

.. code-block:: jinja

    <html>
      <head>
        {{ browserid_css() }}
      </head>
      <body>
        {{ browserid_info() }}
        {% if user.is_authenticated() %}
          <p>Current user: {{ user.email }}</p>
          {{ browserid_logout(text='Logout') }}
        {% else %}
          {{ browserid_login(text='Login', color='dark') }}
        {% endif %}

        <script src="https://code.jquery.com/jquery-1.9.1.min.js"></script>
        {{ browserid_js() }}
      </body>
    </html>

.. _Jinja2: http://jinja.pocoo.org/
.. _jingo: https://github.com/jbalogh/jingo
