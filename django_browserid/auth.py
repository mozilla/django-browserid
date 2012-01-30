import base64
import hashlib
import logging
from warnings import warn

from django.conf import settings
from django.contrib.auth.models import User

from django_browserid.base import get_audience as base_get_audience, verify


log = logging.getLogger(__name__)


def get_audience(*args):
    warn('Deprecated, please use the standalone function '
         'django_browserid.get_audience instead.', DeprecationWarning)
    return base_get_audience(*args)


def default_username_algo(email):
    # store the username as a base64 encoded sha1 of the email address
    # this protects against data leakage because usernames are often
    # treated as public identifiers (so we can't use the email address).
    username = base64.urlsafe_b64encode(
        hashlib.sha1(email).digest()).rstrip('=')
    return username


class BrowserIDBackend(object):
    supports_anonymous_user = False
    supports_object_permissions = False

    def verify(self, *args):
        warn('Deprecated, please use the standalone function '
             'django_browserid.verify instead.', DeprecationWarning)
        return verify(*args)

    def filter_users_by_email(self, email):
        """Return all users matching the specified email."""
        return User.objects.filter(email=email)

    def create_user(self, username, email):
        """Return object for a newly created user account."""
        return User.objects.create_user(username, email)

    def authenticate(self, assertion=None, audience=None):
        """``django.contrib.auth`` compatible authentication method.

        Given a BrowserID assertion and an audience, it attempts to
        verify them and then extract the email address for the authenticated
        user.

        An audience should be in the form ``https://example.com`` or
        ``http://localhost:8001``.

        See django_browserid.base.get_audience()
        """
        result = verify(assertion, audience)
        if result is None:
            return None
        email = result['email']
        # in the rare case that two user accounts have the same email address,
        # log and bail. randomly selecting one seems really wrong.
        users = self.filter_users_by_email(email=email)
        if len(users) > 1:
            log.warn('%d users with email address %s.' % (len(users), email))
            return None
        if len(users) == 1:
            return users[0]
        create_user = getattr(settings, 'BROWSERID_CREATE_USER', False)
        if not create_user:
            return None

        username_algo = getattr(settings, 'BROWSERID_USERNAME_ALGO',
                                default_username_algo)
        user = User.objects.create_user(username_algo(email), email)

        user.is_active = True
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
