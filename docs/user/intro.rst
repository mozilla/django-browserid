Introduction
============

How does it work?
-----------------
At a high level, this is what happens when a user wants to log into a site that
uses django-browserid:

1. A user clicks a login button on your web page.
2. The JavaScript shim (hosted by Persona_) displays a pop-up asking for the
   email address the user wants to log in with.
3. If necessary, the pop-up prompts the user for additional info to
   authenticate them. For example, if the user enters an `@mozilla.com` email,
   the Mozilla LDAP Identity Provider will prompt them for their LDAP password.
4. The JavaScript receives an "assertion" from the Identity Provider and
   submits it to the site's backend via AJAX.
5. The backend sends the assertion to the `Remote verification service`_, which
   verifies the assertion and returns the result, including the email address
   of the user if verification was successful.
6. The backend finds a user account matching that email (creating it if one
   isn't found) and logs the user in as that account.
7. The backend returns a URL that the JavaScript redirects the user to.

Note that this is just an example flow. Several of these steps can be
customized for your site; for example, you may not want user accounts to be
created automatically. This behavior can be changed to suit whatever needs you
have.

A `detailed explanation of the BrowserID protocol`_ is available on MDN.

.. _`detailed explanation of the BrowserID protocol`: https://developer.mozilla.org/Persona/Protocol_Overview
.. _Persona: https://www.persona.org
.. _`Remote Verification Service`: https://developer.mozilla.org/Persona/Remote_Verification_API


.. _persona-dependence:

Persona
-------
By default, django-browserid relies on Persona, which is a set of
BrowserID-related services hosted by Mozilla. It's possible, but annoying, to
use django-browserid without these dependencies.

Currently, django-browserid relies on Persona for:

- The `Cross-browser API Library`_, which implements the ``navigator.id`` API
  for browsers that don't natively support BrowserID.
- The `Fallback Identity Provider`_ for emails from servers that don't support
  BrowserID.
- The `Remote verification service`_, which handles assertion verification for
  sites that don't want to verify assertions themselves.

In the future, django-browserid will remove the need to depend on these
Mozilla-centric services. Local verification and a self-hosted cross-browser
API will greatly reduce the reliance on Mozilla's servers for authentication.

.. _`Cross-browser API Library`: https://developer.mozilla.org/Persona/Bootstrapping_Persona#Cross-browser_API_Library
.. _`Fallback Identity Provider`: https://developer.mozilla.org/Persona/Bootstrapping_Persona#Fallback_Identity_Provider
