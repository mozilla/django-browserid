from django import forms


class BrowserIDForm(forms.Form):
    # A form for the BrowserID Assertion
    # auto_id = False to allow multiple BrowserID Sign-in forms per page

    def __init__(self, *args, **kwargs):
        kwargs.update({'auto_id': False})
        super(BrowserIDForm, self).__init__(*args, **kwargs)

    assertion = forms.CharField(widget=forms.HiddenInput())
