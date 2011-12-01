CHANGELOG
---------

0.9.2a - **API breakage** - BrowserID Train 2011-10-20 now accepts the scheme and port number as part of the audience.

    ``get_audience(host, port)`` has become ``get_audience(request)``
    ``authenticate(assertion, host, port)`` has become ``authenticate(assertion, audience)``

    ``verify`` has been updated, so if you use the basic integration with browserid_verify, you should be fine. This mainly
    breaks sites that have custom account creation or use the ``auth.authenticate`` function.

    To improve security, you should add ``SITE_URL`` to your Django settings. See README.rst for details.

0.9.1 - Create User refactoring, navigator.id, httplib2/verify fixes

    auth.create_user and auth.filter_users_by_email are two integration points which you may wish to override.

0.9.0 - betafarm production release
