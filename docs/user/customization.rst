Customization
=============
Now that you've got django-browserid installed and configured, it's time to see
how to customize it to your needs.


Local Assertion Verification
----------------------------
When a user authenticates via django-browserid, they do so by sending your site
an assertion, which, when verified, gives you an email address for the user.
Normally, this verification is handled by sending the assertion to a
`verification service hosted by Mozilla`_.

However, you can also verify assertions locally and avoid relying on the
verification service. To do so, you must install PyBrowserID_. django-browserid
checks for PyBrowserID, and if it is found, it enables the use of the
:class:`LocalVerifier <django_browserid.LocalVerifier>` class.

Once you've installed PyBrowserID, add the
:class:`LocalBrowserIDBackend <django_browserid.auth.LocalBrowserIDBackend>`
class to your ``AUTHENTICATION_BACKENDS`` setting:

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'django_browserid.auth.LocalBrowserIDBackend',
    )

.. note:: Because the BrowserID certificate format has not been finalized,
          PyBrowserID may fail to verify a valid assertion if the format
          changes. Be aware of the risks before enabling local verification.

.. _`verification service hosted by Mozilla`: https://developer.mozilla.org/en-US/Persona/Remote_Verification_API
.. _PyBrowserID: https://pypi.python.org/pypi/PyBrowserID/


Customizing the Verify View
---------------------------
Many common customizations involve overriding methods on the
:class:`Verify <django_browserid.views.Verify>` class. But how do you use a
custom ``Verify`` subclass?

You can substitute a custom verification view by setting
:attr:`BROWSERID_VERIFY_CLASS <django.conf.settings.BROWSERID_VERIFY_CLASS>` to
the import path for your view:

.. code-block:: python

    BROWSERID_VERIFY_CLASS = 'project.application.views.MyCustomVerifyClass'


Customizing the Authentication Backend
--------------------------------------
Another common way to customize django-browserid is to subclass
:class:`BrowserIDBackend <django_browserid.auth.BrowserIDBackend>`. To use a
custom ``BrowserIDBackend`` class, simply use the python path to your custom
class in the ``AUTHENTICATION_BACKENDS`` setting instead of the path to
``BrowserIDBackend``.


Post-login Response
-------------------
After logging the user in, the default view redirects the user to
:attr:`LOGIN_REDIRECT_URL <django.conf.settings.LOGIN_REDIRECT_URL>` or
:attr:`LOGIN_REDIRECT_URL_FAILURE <django.conf.settings.LOGIN_REDIRECT_URL_FAILURE>`,
depending on if login succeeded or failed. You can modify those settings to
change where they are redirected to.

.. note:: You can use ``django.core.urlresolvers.reverse_lazy`` to generate a
   URL for these settings from a URL pattern name or function name.

You can also override the
:attr:`success_url <django_browserid.views.Verify.success_url>` and
:attr:`failure_url <django_browserid.views.Verify.failure_url>` properties on
the ``Verify`` view if you need more control over how the redirect URLs are
retrieved.

If you need to control the entire response to the ``Verify`` view, such as when
you're :ref:`using custom JavaScript <customjs>`, you'll want to override
:attr:`login_success <django_browserid.views.Verify.login_success>`
and :attr:`login_failure <django_browserid.views.Verify.login_failure>`.


Automatic User Creation
-----------------------
If a user signs in with an email that doesn't match an existing user,
django-browserid automatically creates a new User object for them that is tied
to their email address. You can disable this behavior by setting
:attr:`BROWSERID_CREATE_USER <django.conf.settings.BROWSERID_CREATE_USER>` to
False, which will cause authentication to fail if a user signs in with an
unrecognized email address.

If you want to customize how new users are created (perhaps you want to
generate a display name for them), you can override the
:attr:`create_user <django_browserid.auth.BrowserIDBackend.create_user>` method
on ``BrowserIDBackend``:

.. code-block:: python

    from django_browserid.auth import BrowserIDBackend

    class CustomBackend(BrowserIDBackend):
        def create_user(self, email):
            username = my_custom_username_algo()
            return self.User.objects.create_user(username, email)

.. note:: ``self.User`` points to the User model defined in
   ``AUTH_USER_MODEL`` for custom User model support. See `Custom User Models`_
   for more details.


Limiting Authentication
-----------------------
There are two ways to limit who can authenticate with your site: prohibiting
certain email addresses, or filtering the queryset that emails are compared to.

filter_users_by_email
~~~~~~~~~~~~~~~~~~~~~
:attr:`filter_users_by_email <django_browserid.auth.BrowserIDBackend.filter_users_by_email>`
returns the queryset that is searched when looking for a user account that
matches a user's email. Overriding this allows you to limit the set of users
that are searched:

.. code-block:: python

    from django_browserid.auth import BrowserIDBackend

    class CustomBackend(BrowserIDBackend):
        def filter_users_by_email(self, email):
            # Only allow staff users to login.
            return self.User.objects.filter(email=email, is_staff=True)

.. note:: If you customize ``filter_users_by_email``, you should probably make
   sure that `Automatic User Creation`_ is either disabled or customized to
   only create users that match your limited set.

is_valid_email
~~~~~~~~~~~~~~
:attr:`is_valid_email <django_browserid.auth.BrowserIDBackend.is_valid_email>`
determines if the email a user attempts to log in with is considered valid.
Override this to exclude users with certain emails:

    from django_browserid.auth import BrowserIDBackend

    class CustomBackend(BrowserIDBackend):
        def is_valid_email(self, email):
            # Ignore users from fakeemails.com
            return not email.endswith('@fakeemails.com')


Custom User Models
------------------
Django allows you to `use a custom User model for authentication
<https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model>`_. If you are using a custom User model, and the model has
an ``email`` attribute that can store email addresses, django-browserid should
work out-of-the-box for you.

If this isn't the case, then you will probably have to override the
:attr:`is_valid_email <django_browserid.auth.BrowserIDBackend.is_valid_email>`,
:attr:`filter_users_by_email <django_browserid.auth.BrowserIDBackend.filter_users_by_email>`,
and :attr:`create_user <django_browserid.auth.BrowserIDBackend.create_user>`
methods to work with your custom User class.

.. _custom_user_model: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model


.. _customjs:

Using the JavaScript API
------------------------
django-browserid comes with two JavaScript files to include in your webpage:

1. ``api.js``: An API for triggering logins via BrowserID and verifying
   assertions via the server.

2. ``browserid.js``: A basic example of hooking up links with the JavaScript
   API.

``browserid.js`` only covers basic use cases. If your site has more complex
behavior behind trigger login, you should replace ``browserid.js`` in your
templates with your own JavaScript file that uses the django-browserid
JavaScript API.

.. seealso::

   :js:data:`JavaScript API <django_browserid>`
      API Documentation for ``api.js``.


Django Admin Support
--------------------
If you want to use BrowserID for login on the built-in Django admin interface,
you must use the
:data:`django-browserid admin site <django_browserid.admin.site>` instead of
the default Django admin site:

.. code-block:: python

    from django.contrib import admin

    from django_browserid.admin import site as browserid_admin

    from myapp.foo.models import Bar


    class BarAdmin(admin.ModelAdmin):
        pass
    browserid_admin.register(Bar, BarAdmin)

You must also use the django-browserid admin site in your ``urls.py`` file:

.. code-block:: python

    from django.conf.urls import patterns, include, url

    # Autodiscover admin.py files in your project.
    from django.contrib import admin
    admin.autodiscover()

    # copy_registry copies ModelAdmins registered with the default site, like
    # the built-in Django User model.
    from django_browserid.admin import site as browserid_admin
    browserid_admin.copy_registry(admin.site)

    urlpatterns = patterns('',
        # ...
        url(r'^admin/', include(browserid_admin.urls)),
    )

.. seealso::

   :class:`django_browserid.admin.BrowserIDAdminSite`
      API documentation for BrowserIDAdminSite, including how to customize the
      login page (such as including a normal login alongside BrowserID login).


Alternative Template Languages
------------------------------
By default, django-browserid supports use in Django templates as well as use in
Jinja2_ templates via the jingo_ library. Template helpers are registered as
helper functions with jingo, so you can use them directly in Jinja2 templates:

.. code-block:: jinja

    <div class="authentication">
      {% if user.is_authenticated() %}
        {{ browserid_logout(text='Logout') }}
      {% else %}
        {{ browserid_login(text='Login', color='dark') }}
      {% endif %}
    </div>
    {{ browserid_js() }}

For other libraries or template languages, you will have to register the
django-browserid helpers manually. The relevant helper functions can be found
in the :py:mod:`django_browserid.helpers` module.

.. _Jinja2: http://jinja.pocoo.org/
.. _jingo: https://github.com/jbalogh/jingo
