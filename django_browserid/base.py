import logging
import urllib
from warnings import warn
try:
    import json
except ImportError:
    import simplejson as json


from django.conf import settings

import requests


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
        warn('Using DOMAIN and PROTOCOL to specify your BrowserID audience is '
             'deprecated. Please use the SITE_URL setting instead.',
             DeprecationWarning)

        # DOMAIN is example.com req_domain is example.com:8001
        domain = getattr(settings, 'DOMAIN', req_domain.split(':')[0])
        protocol = getattr(settings, 'PROTOCOL', req_proto)

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


def _verify_http_request(url, qs):
    parameters = {
        'data': qs,
        'proxies': getattr(settings, 'BROWSERID_PROXY_INFO', None),
        'verify': not getattr(settings, 'BROWSERID_DISABLE_CERT_CHECK', False),
        'headers': {'Content-type': 'application/x-www-form-urlencoded'},
        'params': {
            'timeout': getattr(settings, 'BROWSERID_HTTP_TIMEOUT',
                               DEFAULT_HTTP_TIMEOUT)
        }
    }

    if parameters['verify']:
        parameters['verify'] = getattr(settings, 'BROWSERID_CACERT_FILE', True)

    r = requests.post(url, **parameters)

    try:
        rv = json.loads(r.content)
    except ValueError:
        log.debug('Failed to decode JSON. Resp: %s, Content: %s' %
                  (r.status_code, r.content))
        return dict(status='failure')

    return rv


def verify(assertion, audience):
    """Verify assertion using an external verification service."""
    verify_url = getattr(settings, 'BROWSERID_VERIFICATION_URL',
                         DEFAULT_VERIFICATION_URL)

    log.info("Verification URL: %s" % verify_url)

    result = _verify_http_request(verify_url, urllib.urlencode({
        'assertion': assertion,
        'audience': audience
    }))

    if result['status'] == OKAY_RESPONSE:
        return result

    log.error('BrowserID verification failure. Response: %r '
              'Audience: %r' % (result, audience))
    log.error("BID assert: %r" % assertion)
    return False
