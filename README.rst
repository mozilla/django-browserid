================
django-browserid
================

This is ``django-browserid``, a drop-in `Django`_ application that adds support for `BrowserID`_.

.. _Django: http://www.djangoproject.com/
.. _BrowserID: https://browserid.org/

Installation
------------

To use ``django-browserid``, add it to ``INSTALLED_APPS`` in ``settings.py``: ::

   INSTALLED_APPS = (
       # ...
       'django.contrib.auth',
       'django_browserid',  # Load after auth to monkey-patch it.
       # ...
   )

and add ``django_browserid.auth.BrowserIDBackend`` to ``AUTHENTICATION_BACKENDS`` in ``settings.py``: ::

   AUTHENTICATION_BACKENDS = (
       # ...
       'django_browserid.auth.BrowserIDBackend',
       # ...
   )

Edit your ``urls.py`` file and add the following: ::

   urlpatterns = patterns('',
       # ... 
       (r'^browserid/', include('django_browserid.urls')),
       # ...
   )

You can also set the following optional in ``settings.py`` (they have sensible defaults): ::

   # URL of a BrowserID verification service.
   BROWSERID_VERIFICATION_URL = 'https://browserid.org/verify'

   # Create user accounts automatically if no user is found.
   BROWSERID_CREATE_USER = False

   # Path to redirect to on successful login.
   LOGIN_REDIRECT_URL = '/'

   # Path to redirect to on unsuccessful login attempt.
   LOGIN_REDIRECT_URL_FAILURE = '/'

Somewhere in one of your templates, you'll need to create a link and a form with a single hidden input element, which you'll use to submit the BrowserID assertion to the server. If you want to use ``django_browserid.forms.BrowserIDForm``, you could use something like the following HTML snippet: ::

   <a id="browserid" href="{% url gracefully_degrade %}">Sign In</a>
   <form method="POST" action="{% url browserid_verify %}">
      {{ form.as_p }}
   </form>

Finally, you'll need some Javascript to handle the onclick event. If you use ``django_browserid.forms.BrowserID``, you can use the javascript in ``static/browserid.js``. Otherwise, you can use it as a basic example: ::

   $('#browserid').bind('click', function(e) {
     e.preventDefault();
     navigator.getVerifiedEmail(function(assertion) {
       if (assertion) {
         var $e = $('#id_assertion');
         $e.val(assertion.toString());
         $e.parent().submit();
       }
     });
   });

License
-------

This software is licensed under the `New BSD License`_. For more information, read the file ``LICENSE``.

.. _New BSD License: http://creativecommons.org/licenses/BSD/

Status
------

``django-browserid`` is a work in progress. Contributions are welcome. Feel free to `fork`_ and contribute!

.. _fork: https://github.com/mozilla/django-browserid
