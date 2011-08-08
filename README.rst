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

   # CA cert file for validating SSL certificate
   BROWSERID_CACERT_FILE = ''

   # Create user accounts automatically if no user is found.
   BROWSERID_CREATE_USER = False

   # Path to redirect to on successful login.
   LOGIN_REDIRECT_URL = '/'

   # Path to redirect to on unsuccessful login attempt.
   LOGIN_REDIRECT_URL_FAILURE = '/'

Somewhere in one of your templates, you'll need to create a link and a form with a single hidden input element, which you'll use to submit the BrowserID assertion to the server. If you want to use ``django_browserid.forms.BrowserIDForm``, you could use something like the following template snippet: ::

   {% if not user.is_authenticated %}
   <a id="browserid" href="{% url gracefully_degrade %}">Sign In</a>
   <form method="POST" action="{% url browserid_verify %}">
      {{ browserid_form.as_p }}
   </form>
   {% endif %}

If you do this, it is further recommended that you add ``django_browserid.context_processors.browserid_form`` to  ``TEMPLATE_CONTEXT_PROCESSORS``; this will create the ``browserid_form`` variable automatically in ``RequestContext`` instances when needed. That is, in ``settings.py``: ::

   TEMPLATE_CONTEXT_PROCESSORS = (
       # ...
       'django_browserid.context_processors.browserid_form',
       # ...
   )

Finally, you'll need some Javascript to handle the onclick event. If you use ``django_browserid.forms.BrowserIDForm``, you can use the javascript in ``static/browserid.js``. Otherwise, you can use it as a basic example: ::

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

Creating User Accounts
----------------------

``django-browserid`` will automatically create a user account for new users if the setting ``BROWSERID_CREATE_USER`` is set to ``True`` in ``settings.py``. The user account will be created with the verified email returned from the BrowserID verification service, and a URL safe base64 encoded SHA1 of the email with the padding removed as the username. 

If you do not wish to automatically create user accounts, you may manually verify a BrowserID assertion with something like the following: ::

   from django_browserid.auth import get_audience, verify
   from django_browserid.forms import BrowserIDForm


   def myview(request):
      # ...
      if request.method == 'POST':
          form = BrowserIDForm(data=request.POST)
          if not form.is_valid():
              # do something
          host = request.get_host()
          if ':' in host:
              host, port = host.split(':')
          else:
              port = '80'
          audience = get_audience(host, port)
          result = verify(form.cleaned_data['assertion'], audience)
          # ...

``result`` will be False if the assertion failed, or a dictionary similar to the following: ::

   {
      u'audience': u'mysite.com:443',
      u'email': u'myemail@example.com',
      u'issuer': u'browserid.org:443',
      u'status': u'okay',
      u'valid-until': 1311377222765
   }

You are of course then free to store the email in the session and prompt the user to sign up using a chosen identifier as their username, or whatever else makes sense for your site.

License
-------

This software is licensed under the `New BSD License`_. For more information, read the file ``LICENSE``.

.. _New BSD License: http://creativecommons.org/licenses/BSD/

Status
------

``django-browserid`` is a work in progress. Contributions are welcome. Feel free to `fork`_ and contribute!

.. _fork: https://github.com/mozilla/django-browserid
