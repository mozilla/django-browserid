"""
.. data:: user_created

   Signal triggered when the BrowserID authentication backend creates a new
   user. Sender is the function that created the user, user is the new user
   instance.
"""
from django.dispatch import Signal


user_created = Signal(providing_args=['user'])
