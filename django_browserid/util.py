import logging

from django.conf import settings


log = logging.getLogger(__name__)


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
