JavaScript API
==============

The JavaScript file that comes with django-browserid, ``browserid.js``,
includes a a few public functions that are exposed through the
``django_browserid`` global object.


.. js:function:: django_browserid.login([next, requestArgs])

   Manually trigger BrowserID login.

   :param string next: URL to redirect the user to after login.
   :param object requestArgs: Options to pass to `navigator.id.request`_.

.. _`navigator.id.request`: https://developer.mozilla.org/en-US/docs/DOM/navigator.id.request


.. js:function:: django_browserid.logout([next])

   Manually trigger BrowserID logout.

   :param string next: URL to redirect the user to after logout.


.. js:function:: django_browserid.isUserAuthenticated()

   Check if the current user has authenticated via django_browserid. Note that
   this relies on the ``#browserid-info`` element having been loaded into the
   DOM already. If it hasn't, this will return false.

   :returns: True if the user has authenticated, false otherwise.
