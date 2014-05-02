.. :changelog:

History
-------

0.10.1 (2014-05-02)
+++++++++++++++++++
- Add ``browserid_info`` helper back in. The previous method of fetching the
  Persona popup customization via AJAX caused browsers to trigger popup
  warnings when users attempted to log in, so we switched back to the old
  method of adding the info tag to pages.


0.10 (2014-04-15)
+++++++++++++++++
- Massive documentation update, including upgrade instructions for older
  versions.

- Support and test on Python 3.2 and 3.3, and Django 1.6!

- Disable automatic login and logout coming from Persona. This also fixes
  logins being triggered in all open tabs on your site.

- Replace in-page form for trigger logins with AJAX calls. Removes need for
  {% browserid_info %} template tag.

- Drop ``six`` from requirements.

- Replace ``SITE_URL`` setting with ``BROWSERID_AUDIENCES`` and make it
  optional when ``DEBUG`` is True.

- Add support for logging-in to the admin interface with Persona.

- Remove need to set custom context processor.

- Replace ``verify`` function with the Verifier classes like
  ``RemoteVerifier``.

- And more!


0.9 (2013-08-25)
++++++++++++++++
- Add ``BROWSERID_VERIFY_CLASS`` to make it easier to customize the verification view.

- Add hook to authentication backend for validating the user's email.

- Ensure backend attribute exists on user objects authenticated by django-browserid.

- Prevent installation of the library as an unpackaged egg.

- Add incomplete Python 3 support.

- Fix an issue where users who logged in without Persona were being submitted to
  ``navigator.id.watch`` anyway.

- Add CSS to make the login/logout buttons prettier.

- Support for ``SITE_URL`` being an iterable.

- Add support for lazily-evaluated ``BROWSERID_REQUEST_ARGS``.

- Add a small JavaScript API available on pages that include ``browserid.js``.

- Support running tests via `python setup.py test`.

- Fix an infinite loop where logging in with a valid Persona account while
  ``BROWSERID_CREATE_USER`` is true would cause an infinite redirection.


0.8 (2013-03-05)
++++++++++++++++

- #97: Add BrowserIDException that is raised by verify when there are issues
  connecting to the remote verification service. Update the Verify view to handle
  these errors.

- #125: Prevent the Verify view from running reverse on user input and add check
  to not redirect to URLs with a different host.

- Remove ability to set a custom name for the Verify redirect parameter: it's
  just ``next``.

- Replace ``browserid_button`` with ``browserid_login`` and
  ``browserid_logout``, and make ``browserid_info`` a function.

- #109: Fix issue with unicode strings in the ``extra_params`` kwarg for
  ``verify``.

- #110: Fix bug where kwargs to ``authenticate`` get passed as ``extra_params``
  to verify. Instead, you can pass any extra parameters in ``browserid_extra``.
  But please don't, it's undocumented for a reason. <3

- #105: General documentation fixes, add more debug logging for common issues.
  Add ``BROWSERID_DISABLE_SANITY_CHECKS`` setting and remove the need to set
  ``SITE_URL`` in development.

- Add ``form_extras`` parameter to ``browserid_button``.

- #101, #102: Update the default JavaScript to pass the current user's email
  address into ``navigator.id.watch`` to avoid unnecessary auto-login attempts.

- Add template functions/tags to use for embedding login/logout buttons instead
  of using your own custom HTML.

- Add a ``url`` kwarg to ``verify`` that lets you specify a custom verification
  service to use.

- Add documentation for setting up the library for development.

- #103: ``BrowserIDForm`` now fails validation if the assertion given is
  non-ASCII.

- Fix an error in the sample urlconf in the documentation.

- #98: Fix a bug where login or logout buttons might not be detected by the
  default JavaScript correctly if ``<a>`` element contained extra HTML.

- Add ``pass_mock`` kwarg to ``mock_browserid``, which adds a new argument to
  the front of the decorated method that is filled with the Mock object used
  in place of ``_verify_http_request``.

- Any extra kwargs to ``BrowserIDBackend.authenticate`` are passed in the verify
  request as POST arguments (this will soon be removed, don't rely on it).

0.7.1 (2012-11-08)
++++++++++++++++++

- Add support for a working logout button. Switching to the Observer API in 0.7
  made the issue that we weren't calling ``navigator.id.logout`` more
  pronounced, so it makes sense to make a small new release to make it easier
  to add a logout button.

0.7 (2012-11-07)
++++++++++++++++
- Actually start updating the Changelog again.

- Remove deprecated functions ``django_browserid.auth.get_audience`` and
  ``django_browserid.auth.BrowserIDBackend.verify``, as well as support for
  ``DOMAIN`` and ``PROTOCOL`` settings.

- Add small fix for infinite login loops.

- Add automated testing for Django 1.3.4, 1.4.2, and 1.5a1.

- Switch to using ``format`` for all string formatting (**breaks Python 2.5
  compatibility**).

- Add support for Django 1.5 Custom User Models.

- Fix request timeouts so that they work properly.

- Add ability to customize BrowserID login popup via arguments to
  ``navigator.id.request``.

- Update JavaScript to use the new Observer API.

- Change ``browserid.org`` urls to ``login.persona.org``.
