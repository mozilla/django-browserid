"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from django import forms


class BrowserIDForm(forms.Form):
    assertion = forms.CharField(widget=forms.HiddenInput())

    class Media:
        js = ('browserid/browserid.js', 'https://login.persona.org/include.js')

    def clean_assertion(self):
        try:
            return str(self.cleaned_data['assertion'])
        except UnicodeEncodeError:
            # not ascii :(
            raise forms.ValidationError('non-ascii string')
