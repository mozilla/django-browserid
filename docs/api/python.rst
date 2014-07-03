Python API
==========
This part of the documentation describes the interfaces for using
django-browserid.


.. py:module:: django_browserid

.. _template-helpers:

Template Helpers
----------------
.. py:module:: django_browserid.helpers

Template helpers are the functions used in your templates that output HTML for
login and logout buttons, as well as the CSS and JS tags for making the buttons
function and display correctly.

.. autofunction:: browserid_info

.. autofunction:: browserid_login

.. autofunction:: browserid_logout

.. autofunction:: browserid_js

.. autofunction:: browserid_css


Admin Site
----------
.. py:module:: django_browserid.admin

Admin site integration allows you to support login via django-browserid on the
Django built-in admin interface.

.. autoclass:: BrowserIDAdminSite
   :members: include_password_form, copy_registry

.. autodata:: site
   :annotation:


Authentication Backends
-----------------------
.. py:module:: django_browserid.auth

There are a few different authentication backends to choose from depending on
how you want to authenticate users.

.. autoclass:: BrowserIDBackend
   :members:

.. autoclass:: LocalBrowserIDBackend
   :show-inheritance:


Views
-----
.. py:module:: django_browserid.views

django-browserid works primarily through AJAX requests to the views below in
order to log users in and out and to send information required for the login
process, such as a CSRF token.

.. autoclass:: Verify
   :members:
   :show-inheritance:

.. autoclass:: Logout
   :members:
   :show-inheritance:

.. autoclass:: CsrfToken
   :members:
   :show-inheritance:


Signals
-------
.. py:module:: django_browserid.signals

.. autodata:: user_created
   :annotation:


Exceptions
----------
.. autoexception:: django_browserid.base.BrowserIDException
   :members:


Verification
------------
.. py:currentmodule:: django_browserid

The verification classes allow you to verify if a user-provided assertion is
valid according to the Identity Provider specified by the user's email address.
Generally you don't have to use these directly, but they are available for
sites with complex authentication needs.

.. autoclass:: django_browserid.RemoteVerifier
   :members: verify

.. autoclass:: django_browserid.LocalVerifier
   :members: verify

.. autoclass:: django_browserid.MockVerifier
   :members: __init__, verify

.. autoclass:: django_browserid.VerificationResult
   :members: expires

.. autofunction:: django_browserid.get_audience
