# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms
from django.conf import settings


FORM_JAVASCRIPT = ('browserid/browserid.js',)
BROWSERID_SHIM = getattr(settings, 'BROWSERID_SHIM',
                         'https://login.persona.org/include.js')


class BrowserIDForm(forms.Form):
    assertion = forms.CharField(widget=forms.HiddenInput())
    next = forms.CharField(required=False, widget=forms.HiddenInput())

    class Media:
        js = FORM_JAVASCRIPT + (BROWSERID_SHIM,)

    def clean_assertion(self):
        try:
            return str(self.cleaned_data['assertion'])
        except UnicodeEncodeError:
            # not ascii :(
            raise forms.ValidationError('non-ascii string')
