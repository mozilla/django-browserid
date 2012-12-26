Advanced Usage
==============

navigator.id.request Arguments
------------------------------

The ``navigator.id.request`` function accepts several optional arguments that
customize the BrowserID login dialog. The default JavaScript provided by
``django-browserid`` checks for data attributes on the login link and passes
them to ``navigator.id.request``. For example, the following customizes the
website name shown in the BrowserID dialog::

    <a href="#" data-site-name="Site Name">Login</a>

.. note:: ``navigator.id.request`` arguments are in camelCase, but data
   attributes must use dashes in place of capitalization changes.

See the `navigator.id.request documentation`_ for a list of accepted parameters.

.. _navigator.id.request documentation: https://developer.mozilla.org/docs/DOM/navigator.id.request

Automatic Account Creation
--------------------------

``django-browserid`` will automatically create a user account for new
users. The user account will be created with the verified
email returned from the BrowserID verification service, and a URL safe
base64 encoded SHA1 of the email with the padding removed as the
username.

To provide a customized username, you can provide a different
algorithm via your settings.py::

   # settings.py
   BROWSERID_CREATE_USER = True
   def username(email):
       return email.rsplit('@', 1)[0]
   BROWSERID_USERNAME_ALGO = username

You can can provide your own function to create users by setting
``BROWSERID_CREATE_USER`` to a string path pointing to a function::

   # module/util.py
   def create_user(email):
       return User.objects.create_user(email, email)

   # settings.py
   BROWSERID_CREATE_USER = 'module.util.create_user'

You can disable account creation, but continue to use the
``browserid_verify`` view to authenticate existing users with the
following::

    BROWSERID_CREATE_USER = False


Custom Verification
-------------------

If you want full control over account verification, don't use
django-browserid's ``browserid_verify`` view. Create your own view and
use :func:`django_browserid.verify` to manually verify a
BrowserID assertion with something like the following::

   from django_browserid import get_audience, verify
   from django_browserid.forms import BrowserIDForm


   def myview(request):
      # ...
      if request.method == 'POST':
          form = BrowserIDForm(data=request.POST)
          if not form.is_valid():
              result = verify(form.cleaned_data['assertion'], get_audience(request))
              if result:
                  # check for user account, create account for new users, etc
                  user = my_get_or_create_user(result.email)

``result`` will be ``False`` if the assertion failed, or a dictionary
similar to the following::

   {
      u'audience': u'https://mysite.com:443',
      u'email': u'myemail@example.com',
      u'issuer': u'browserid.org',
      u'status': u'okay',
      u'expires': 1311377222765
   }

You are of course then free to store the email in the session and
prompt the user to sign up using a chosen identifier as their
username, or whatever else makes sense for your site.


Javascript Fallback
-------------------

It is a good idea to provide an alternative method of authenticating with your
site for users that do not have JavaScript available. An easy way of doing this
is to modify the ``href`` of the link that you bind to BrowserID login to point
to a traditional login and registration page::

   <a id="browserid" href="{% url 'login.view.name' %}">Sign In</a>

If a user has JavaScript enabled, when they click the link the JavaScript will
take over and show a BrowserID popup. If a user has JavaScript disabled, they
will be directed to your login view (which should not require JavaScript, of
course).


Multiple Login Buttons
----------------------

If you are using the default JavaScript provided by ``django-browserid``, you
can have multiple login buttons on a single page by marking them with the class
``browserid-login``. Be sure to only include the hidden login form on the page
once to avoid errors from using the same id multiple times.


Signals
-------

.. module:: django_browserid.signals

.. data:: user_created

    Signal triggered when a user is automatically created during authentication.

    * **sender**: The function that created the user instance.
    * **user**: The user instance that was created.

API
----------

.. autofunction:: django_browserid.verify

.. autofunction:: django_browserid.get_audience


Custom User Model
-----------------

Django 1.5 allows you to specify a custom model to use in place of the built-in
User model with the ``AUTH_USER_MODEL`` setting. ``django-browserid`` supports
custom User models, however you will most likely need to subclass
``django-browserid.BrowserIDBackend`` and override the ``create_user``,
``get_user``, and ``filter_users_by_email`` functions to work with your class.
