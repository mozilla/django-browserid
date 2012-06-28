"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

.. data:: user_created

   Signal triggered when the BrowserID authentication backend creates a new
   user. Sender is the function that created the user, user is the new user
   instance.
"""
from django.dispatch import Signal


user_created = Signal(providing_args=['user'])
