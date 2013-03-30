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

.. note:: ``TEMPLATE_CONTEXT_PROCESSORS`` is not in the settings file by
   default. You can find the default value in the `Context Processor
   documentation`_.

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

1. ``{% browserid_info %}``: Outputs an invisible element that stores info about
   the current user. Must be within the ``<body>`` tag and appear only **once**.

2. ``{% browserid_js %}``: Outputs the ``<script>`` tags for the button
   JavaScript. Must be somewhere on the page, typically at the bottom right
   before the ``</body>`` tag to allow the page to visibly load before
   executing.

3. ``{% browserid_login %}`` and ``{% browserid_logout %}``: Outputs the HTML
   for the login and logout buttons.

.. note:: The ``{% browserid_login %}`` template tag takes an optional *image*
  parameter to display the official Persona branded sign in buttons. The image
  names are the same as those found on the `Persona site <https://developer.mozilla.org/en-US/docs/persona/branding>`_.

  Example: ``{% browserid_login image='plain_sign_in_red.png' %}``

  The images are included with the library.


A complete example:

.. code-block:: html+django

    {% load browserid %}
    <html>
      <body>
        {% browserid_info %}
        <header>
          <h1>My Site</h1>
          <div class="authentication">
            {% if user.is_authenticated %}
              {% browserid_logout text='Logout' %}
            {% else %}
              {% browserid_login text='Login' %}
            {% endif %}
          </div>
        </header>
        <article>
          <p>Welcome to my site!</p>
        </article>
        <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
        {% browserid_js %}
      </body>
    </html>

If you're using `Jinja2`_ as your templating system, you can use the functions
passed to your template by the context processor:

.. code-block:: html+jinja

    <html>
      <body>
        {{ browserid_info() }}
        <header>
          <h1>My Site</h1>
          <div class="authentication">
            {% if user.is_authenticated() %}
              {{ browserid_logout(text='Logout') }}
            {% else %}
              {{ browserid_login(text='Login') }}
            {% endif %}
          </div>
        </header>
        <article>
          <p>Welcome to my site!</p>
        </article>
        <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
        {{ browserid_js() }}
      </body>
    </html>

.. note:: The JavaScript assumes you have `jQuery`_ 1.7 or higher on your site.

.. note:: For more information about the template helper functions, check out
   the :doc:`details/api` document.

.. _jQuery: http://jquery.com/
.. _Jinja2: http://jinja.pocoo.org/
.. _`Context Processor documentation`: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors


Deploying to Production
-----------------------
There are a few changes you need to make when deploying your app to production:

- BrowserID uses an assertion and an audience to verify the user. The
  ``SITE_URL`` setting is used to determine the audience. For security reasons,
  it is *very important* that you set ``SITE_URL`` correctly.

   ``SITE_URL`` should be set to the domain and protocol users will use to
   access your site, such as ``https://affiliates.mozilla.org``. This URL does
   not have to be publicly available, however, so sites limited to a certain
   network can still use django-browserid.


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

If you are using the optional Persona branded images you need to make sure they are uploaded with the static files. 

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


Alternate Template Languages (Jingo/Jinja)
------------------------------------------
If you are using a library like `Jingo`_ in order to use a template language
besides the Django template language, you may need to configure the library to
use the Django template language for django-browserid templates. With Jingo,
you can do this using the ``JINGO_EXCLUDE_APPS`` setting::

    JINGO_EXCLUDE_APPS = ('browserid',)

.. _Jingo: https://github.com/jbalogh/jingo


Troubleshooting Issues
----------------------
If you run into any issues while setting up django-browserid, try the following
steps:

1. Check for any warnings in the server log. You may have to edit your
   development server's logging settings to output ``django_browserid`` log
   entries. Here's an example ``LOGGING`` setup to start with::

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

2. Check the :doc:`details/troubleshooting` document for commonly-reported
   issues.

3. Ask for help in the `#webdev`_ channel on irc.mozilla.org.

4. Post an issue on the `django-browserid Issue Tracker`_.

.. _#webdev: http://chat.mibbit.com/?channel=%23chat&server=irc.mozilla.org
.. _django-browserid Issue Tracker: https://github.com/mozilla/django-browserid/issues
