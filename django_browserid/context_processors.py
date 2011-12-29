from django_browserid.forms import BrowserIDForm


def browserid_form(request):
    """
    A context processor that adds a BrowserID form to the request
    """
    return {'browserid_form': BrowserIDForm()}
