.. :changelog:

History
-------

Latest
++++++

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
