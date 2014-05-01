JavaScript API
==============
This part of the documentation describes the JavaScript API defined in
``api.js`` that can be used to interact with Persona or the
django-browserid views on your server.


.. js:data:: django_browserid

   Global object containing the JavaScript API for interacting with
   django-browserid.

   Most functions return `jQuery Deferreds`_ for registering asynchronous
   callbacks.

   .. _`jQuery Deferreds`: https://api.jquery.com/jQuery.Deferred/


   .. js:function:: login([requestArgs])

      Retrieve an assertion and use it to log the user into your site.

      :param object requestArgs: Options to pass to `navigator.id.request`_.
      :returns: Deferred that resolves once the user has been logged in.

   .. _`navigator.id.request`: https://developer.mozilla.org/en-US/docs/DOM/navigator.id.request


   .. js:function:: logout()

      Log the user out of your site.

      :returns: Deferred that resolves once the user has been logged out.


   .. js:function:: getAssertion([requestArgs])

      Retrieve an assertion via BrowserID.

      :returns: Deferred that resolves with the assertion once it is retrieved.


   .. js:function:: verifyAssertion(assertion)

      Verify that the given assertion is valid, and log the user in.

      :param string assertion: Assertion to verify.
      :returns: Deferred that resolves with the login view response once login
                is complete.


   .. js:function:: getInfo()

      Fetch information from the
      :func:`browserid_info <django_browserid.helpers.browserid_info>` tag,
      such as the parameters for the Persona popup.

      :returns: Object containing the data from the info tag.


   .. js:function:: getCsrfToken()

      Fetch a CSRF token from the
      :attr:`CsrfToken view <django_browserid.views.CsrfToken>` via an AJAX
      request.

      :returns: Deferred that resolves with the CSRF token.


   .. js:function:: didLoginFail([location])

      Check for the query string parameter used to signal a failed login.

      :param string location: Location object containing the URL to check.
                              Defaults to ``window.location``.
      :returns: True if the parameter was found and login failed, false
                otherwise.
