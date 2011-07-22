from django import forms


class BrowserIDForm(forms.Form):
    assertion = forms.CharField(widget=forms.HiddenInput())
