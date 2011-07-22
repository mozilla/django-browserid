try:
    import json
except ImportError:
    import simplejson as json

import base64
import hashlib
import logging
import urllib

import httplib2

from django.conf import settings
from django.contrib.auth.models import User

log = logging.getLogger(__name__)

DEFAULT_HTTP_PORT = '80'
DEFAULT_VERIFICATION_URL = 'https://browserid.org/verify'
OKAY_RESPONSE = 'okay'


class BrowserIDBackend(object):
    supports_anonymous_user = False
    supports_object_permissions = False

    def get_audience(self, host, port):
        if port and port != DEFAULT_HTTP_PORT:
            return u'%s:%s' % (host, port)
        return host

    def verify(self, assertion, audience):
        """Verify assertion using an external verification service."""
        verify_url = getattr(settings, 'BROWSERID_VERIFICATION_URL',
                             DEFAULT_VERIFICATION_URL)
        client = httplib2.Http()
        response, content = client.request('%s?%s' % (verify_url,
            urllib.urlencode(dict(assertion=assertion, audience=audience))),
            'POST')
        result = json.loads(content)
        if result['status'] == OKAY_RESPONSE:
            return result
        return False

    def authenticate(self, assertion=None, host=None, port=None):
        result = self.verify(assertion, self.get_audience(host, port))
        if result is None:
            return None
        email = result['email']
        # in the rare case that two user accounts have the same email address,
        # log and bail. randomly selecting one seems really wrong.
        users = User.objects.filter(email=email)
        if len(users) > 1:
            log.warn('%d users with email address %s.' % (len(users), email))
            return None
        if len(users) == 1:
            return users[0]
        create_user = getattr(settings, 'BROWSERID_CREATE_USER', False)
        if not create_user:
            return None
        # store the username as a base64 encoded sha1 of the email address
        # this protects against data leakage because usernames are often
        # treated as public identifiers (so we can't use the email address).
        username = base64.urlsafe_b64encode(
            hashlib.sha1(email).digest()).rstrip('=')
        user = User.objects.create_user(username, email)
        user.is_active = True
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
