try:
    import json
except ImportError:
    import simplejson as json

import logging
import urllib

from django.conf import settings

import httplib2


log = logging.getLogger(__name__)


DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_VERIFICATION_URL = 'https://browserid.org/verify'
OKAY_RESPONSE = 'okay'


def _verify_http_request(url, qs):
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


def verify(assertion, audience):
    """Verify assertion using an external verification service."""
    verify_url = getattr(settings, 'BROWSERID_VERIFICATION_URL',
                         DEFAULT_VERIFICATION_URL)
    result = _verify_http_request(verify_url, urllib.urlencode({
        'assertion': assertion,
        'audience': audience
    }))
    if result['status'] == OKAY_RESPONSE:
        return result
    log.error("BrowserID verification failure. Assertion: %r Audience: %r"
              " Response: %r" % (assertion, audience, result))
    return False
