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


def get_audience(request):
    """Uses Django settings to format the audience.

    To use this function, make sure there is either a SITE_URL in
    your settings.py file or PROTOCOL and DOMAIN.

    Examples using SITE_URL:
        SITE_URL = 'http://127.0.0.1:8001'
        SITE_URL = 'https://example.com'
        SITE_URL = 'http://example.com'

    If you don't have a SITE_URL you can also use these varables:
    PROTOCOL, DOMAIN, and (optionally) PORT.
    Example 1:
        PROTOCOL = 'https://'
        DOMAIN = 'example.com'

    Example 2:
        PROTOCOL = 'http://'
        DOMAIN = '127.0.0.1'
        PORT = '8001'

    If none are set, we trust the request to populate the audience.
    This is *not secure*!
    """
    site_url = getattr(settings, 'SITE_URL', False)

    # Note audience based on request for developer warnings
    if request.is_secure():
        req_proto = 'https://'
    else:
        req_proto = 'http://'
    req_domain = request.get_host()

    # If we don't define it explicitly
    if not site_url:
        protocol = getattr(settings, 'PROTOCOL', req_proto)
        if not getattr(settings, 'DOMAIN'):
            log.warning('django-browserid WARNING you are missing '
                        'settings.SITE_URL. This is not a secure way '
                        'to verify assertions. Please fix me. '
                        'Setting domain to %s.' % req_domain)

        # DOMAIN is example.com req_domain is example.com:8001
        domain = getattr(settings, 'DOMAIN', req_domain.split(':')[0])

        standards = {'https://': 443, 'http://': 80}
        if ':' in req_domain:
            req_port = req_domain.split(':')[1]
        else:
            req_port = None
        port = getattr(settings, 'PORT', req_port or standards[protocol])
        if port == standards[protocol]:
            site_url = ''.join(map(str, (protocol, domain)))
        else:
            site_url = ''.join(map(str, (protocol, domain, ':', port)))

    req_url = "%s%s" % (req_proto, req_domain)
    if site_url != "%s%s" % (req_proto, req_domain):
        log.warning('Misconfigured SITE_URL? settings has [%s], but '
                    'actual request was [%s] BrowserID may fail on '
                    'audience' % (site_url, req_url))
    return site_url


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

        try:
            rv = json.loads(content)
        except ValueError:
            log.debug('Failed to decode JSON. Resp: %s, Content: %s' % (
                resp, content))
            return dict(status='failure')

        return rv

    def verify(self, assertion, audience):
        """Verify assertion using an external verification service."""
        verify_url = getattr(settings, 'BROWSERID_VERIFICATION_URL',
                             DEFAULT_VERIFICATION_URL)

        log.info("Verification URL: %s" % verify_url)

        result = self._verify_http_request(verify_url, urllib.urlencode({
            'assertion': assertion,
            'audience': audience
        }))
        if result['status'] == OKAY_RESPONSE:
            return result
        log.error("BrowserID verification failure. Response: %r"
                  " Audience: %r" % (result, audience))
        log.error("BID assert: %r" % assertion)
        return False

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

        See django_browserid.auth.get_audience()
        """
        result = self.verify(assertion, audience)
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
