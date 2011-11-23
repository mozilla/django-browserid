from django_browserid.forms import BrowserIDForm


def browserid_form(request):
    """
    A context processor that adds a BrowserID form to the request
    when the user is not authenticated
    """
    if request.user.is_authenticated():
        return {}
    else:
        return {'browserid_form': BrowserIDForm()}
