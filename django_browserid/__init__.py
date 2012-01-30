from django_browserid.auth import BrowserIDBackend
from django_browserid.base import get_audience, verify


VERSION = (0, 1)
__version__ = '.'.join(map(str, VERSION))
