.. :changelog:

History
-------

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
