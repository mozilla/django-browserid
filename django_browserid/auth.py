
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

DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_VERIFICATION_URL = 'https://browserid.org/verify'
OKAY_RESPONSE = 'okay'


class BrowserIDBackend(object):
    supports_anonymous_user = False
    supports_object_permissions = False

    def get_audience(self, host, https):
        if https:
            scheme = 'https'
            default_port = 443
        else:
            scheme = 'http'
            default_port = 80

        audience = "%s://%s" % (scheme, host)
        if ':' in host:
            return audience
        else:
            return "%s:%s" % (audience, default_port)

    def _verify_http_request(self, url, qs):
        params = {'timeout': getattr(settings, 'BROWSERID_HTTP_TIMEOUT',
                                     DEFAULT_HTTP_TIMEOUT)}

        proxy_info = getattr(settings, 'BROWSERID_PROXY_INFO', None)
        if proxy_info:
            params['proxy_info'] = proxy_info

        ca_certs = getattr(settings, 'BROWSERID_CACERT_FILE', None)
        if ca_certs:
            params['ca_certs'] = ca_certs

        disable_cert_check = getattr(settings,
                                     'BROWSERID_DISABLE_CERT_CHECK',
                                     False)
        if disable_cert_check:
            params['disable_ssl_certificate_validation'] = disable_cert_check

        client = httplib2.Http(**params)

        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        resp, content = client.request(url, 'POST', body=qs, headers=headers)

        return json.loads(content)

    def verify(self, assertion, audience):
        """Verify assertion using an external verification service."""
        verify_url = getattr(settings, 'BROWSERID_VERIFICATION_URL',
                             DEFAULT_VERIFICATION_URL)
        result = self._verify_http_request(verify_url, urllib.urlencode({
            'assertion': assertion,
            'audience': audience
        }))
        if result['status'] == OKAY_RESPONSE:
            return result
        log.error("BrowserID verification failure. Assertion: %r Audience: %r"
                  " Response: %r" % (assertion, audience, result))
        return False

    def filter_users_by_email(self, email):
        """Return all users matching the specified email."""
        return User.objects.filter(email=email)

    def create_user(self, username, email):
        """Return object for a newly created user account."""
        return User.objects.create_user(username, email)

    def authenticate(self, assertion=None, host=None, https=None):
        result = self.verify(assertion, self.get_audience(host, https))
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
        # store the username as a base64 encoded sha1 of the email address
        # this protects against data leakage because usernames are often
        # treated as public identifiers (so we can't use the email address).
        username = base64.urlsafe_b64encode(
            hashlib.sha1(email).digest()).rstrip('=')
        user = self.create_user(username, email)
        user.is_active = True
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
