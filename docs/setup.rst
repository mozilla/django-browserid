Setup
=====

Requirements
------------

You can use pip to install required libraries:

   pip install -r requirements.txt

Installation
------------

To use ``django-browserid``, add it to ``INSTALLED_APPS`` in ``settings.py``::

   INSTALLED_APPS = (
       # ...
       'django.contrib.auth',
       'django_browserid',  # Load after auth to monkey-patch it.
       # ...
   )

and add ``django_browserid.auth.BrowserIDBackend`` to ``AUTHENTICATION_BACKENDS`` in ``settings.py``::

   AUTHENTICATION_BACKENDS = (
       # ...
       'django_browserid.auth.BrowserIDBackend',
       # ...
   )

Edit your ``urls.py`` file and add the following::

   urlpatterns = patterns('',
       # ...
       (r'^browserid/', include('django_browserid.urls')),
       # ...
   )

You should also add the following in ``settings.py``::

    # Note: No trailing slash
    SITE_URL = 'https://example.com:8000'

BrowserID uses an assertion and an audience to verify the user. This
``SITE_URL`` is used to determine the audience. For security reasons, it is
*very important* that you set ``SITE_URL`` correctly.

You can also set the following optional config in ``settings.py``
(they have sensible defaults): ::

   # Path to redirect to on successful login.
   LOGIN_REDIRECT_URL = '/'

   # Path to redirect to on unsuccessful login attempt.
   LOGIN_REDIRECT_URL_FAILURE = '/'

   # Create user accounts automatically if no user is found.
   BROWSERID_CREATE_USER = True

Somewhere in one of your templates, you'll need to create a link and a
form with a single hidden input element, which you'll use to submit
the BrowserID assertion to the server. If you want to use
``django_browserid.forms.BrowserIDForm``, you could use something like
the following template snippet: ::

   {% if not user.is_authenticated %}
   <a id="browserid" href="{% url gracefully_degrade %}">Sign In</a>
   <form method="POST" action="{% url browserid_verify %}">
      {% csrf_token %}
      {{ browserid_form.as_p }}
   </form>
   {% endif %}

If you use browserid_form, it is further recommended that you add
``django_browserid.context_processors.browserid_form`` to
``TEMPLATE_CONTEXT_PROCESSORS``; this will create the
``browserid_form`` variable automatically in ``RequestContext``
instances when needed. That is, in ``settings.py``::

   TEMPLATE_CONTEXT_PROCESSORS = (
       # ...
       'django_browserid.context_processors.browserid_form',
       # ...
   )

You will also need to include JavaScript to power the BrowserID popup
and form. You can use django form media at the bottom of your page
(see `Form Media`_ and `Managing static files`_ for more
information)::

   {{ browserid_form.media }}

.. note:: If you don't want to use the static files framework, you'll need to
   include the ``https://browserid.org/include.js`` file, as well as
   JavaScript similar to ``django_browserid/static/browserid/browserid.js``::

      <script src="https://browserid.org/include.js"></script>
      <!-- Include JS for browserid_form here. -->

.. _Form Media: https://docs.djangoproject.com/en/1.3/topics/forms/media/
.. _Managing static files: https://docs.djangoproject.com/en/1.3/howto/static-files/
