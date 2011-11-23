CHANGELOG
---------

0.9.2 - *NOTE* get_audience API breakage - Train 2011-10-20 now accepts the scheme and port number as part of the audience.

    get_audience(self, host, port) has become get_audience(self, request, host, port)

0.9.1 - Create User refactoring, navigator.id, httplib2/verify fixes

    auth.create_user and auth.filter_users_by_email are two integration points which you may wish to override.

0.9.0 - betafarm production release
