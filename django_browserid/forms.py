from django import forms


class BrowserIdForm(forms.Form):
    assertion = forms.CharField(widget=forms.HiddenInput())
