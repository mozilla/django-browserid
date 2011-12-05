from django_browserid.auth import BrowserIDBackend
from django_browserid.base import verify
from django_browserid.util import get_audience

VERSION = (0, 1)
__version__ = '.'.join(map(str, VERSION))
